from __future__ import annotations
import signal
import asyncio
from getpass import getpass
import os
from typing import Any, Dict, Optional
from pydantic import BaseModel

from .schemas.pydanticobjectid import PydanticObjectId
from websockets.client import connect

from .APIError import APIError
from .BaseAPIClient import BaseAPIClient
from .singleton import Singleton


def remove_empties_from_dict(d: Dict | None):
    if not isinstance(d, dict):
        return d
    new_dict = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = remove_empties_from_dict(v)
        if v is not None:
            new_dict[k] = v
    return new_dict or None


class Params(BaseModel):
    offset: int | None = None
    limit: int | None = None


class APIClient(BaseAPIClient, metaclass=Singleton):
    _API_NAME = "Zeit API"  # type: ignore

    def __init__(self, username=None, password=None, token=None, base_url=None):
        super(APIClient, self).__init__()
        self.base_url = base_url or os.environ.get(
            "API_BASE_URL", "https://dev.tempzeit.com"
        )
        self.username = username
        self.password = password or os.environ.get("PASSWORD")
        self.token = token or os.environ.get("AUTH_TOKEN")
        if username and password or token:
            self.authenticated = self._authenticate(
                self.username, self.password, self.token
            )

    def __repr__(self):
        if self.username:
            return f"Client(user={self.username})"
        else:
            return "Client(TOKEN)"

    def _authenticate(
        self, username: Optional[str], password: Optional[str], token: Optional[str]
    ):
        """Authenticate with the Zeit API.

        There are two ways of authenticating:
            1. Username and password. Use this to authenticate a user.
            2. API token. Use this to authenticate an application that is
                not associated with a user

        Args:
            username: Login credential set during Zeit registration
            password: Password for login
            token: Authentication token; may be passed instead of username and password
        """
        if username:
            self.username = username
            self.password = password or getpass()

            res = self._post(
                f"{self.base_url}/auth/login",
                data={"username": self.username, "password": self.password},
                headers={},
            )

            self.token = res["access_token"]
            os.environ["AUTH_TOKEN"] = self.token
            self.requests_session.headers.update(
                {"Authorization": f"Bearer {self.token}"}
            )

        elif token:
            self.requests_session.headers.update({"authorization": str(self.token)})

        else:
            raise APIError(
                "auth/login",
                403,
                "Authentication failed: Username or token must be provided.",
            )
        return True

    def login(self, username: str, password: str):
        return self._authenticate(username=username, password=password, token=None)

    def logout(self):
        return self._post(f"{self.base_url}/auth/logout")

    def register_user(self, body):
        return self._post(f"{self.base_url}/auth/register", json=body)

    def request_verify_token(self, email: str):
        return self._post(
            f"{self.base_url}/auth/request-verify-token", json={"email": email}
        )

    def get_user(self, id: PydanticObjectId):
        return self._get(f"{self.base_url}/users/{id}")

    def get_user_loops(self, id: PydanticObjectId):
        return self._get(f"{self.base_url}/users/{id}/loops")

    def get_users(
        self,
        email: str | None = None,
        loop_id: PydanticObjectId | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        params = remove_empties_from_dict(
            {
                "loop_id": loop_id,
                "limit": limit,
                "offset": offset,
                "email": email,
            }
        )
        return self._get(f"{self.base_url}/users", params=params)

    def patch_user(self, id: PydanticObjectId, body: Dict[str, Any]):
        return self._patch(f"{self.base_url}/users/{id}", json=body)

    def delete_user(self, id: str):
        return self._delete(f"{self.base_url}/users/{id}")

    def create_loop(self, body: Dict[str, Any]):
        return self._post(f"{self.base_url}/loops", json=body)

    def patch_loop(self, id: PydanticObjectId, body: Dict[str, Any]):
        return self._patch(f"{self.base_url}/loops/{id}", json=body)

    def delete_loop(self, id: PydanticObjectId):
        return self._delete(f"{self.base_url}/loops/{id}")

    def get_loop(self, id: PydanticObjectId):
        return self._get(f"{self.base_url}/loops/{id}")

    def get_loops(
        self,
        name: str | None = None,
        status: str | None = None,
        type: str | None = None,
        limit: int = 999,
        offset: int = 0,
    ):
        params = remove_empties_from_dict(
            {
                "name": name,
                "status": status,
                "type": type,
                "limit": limit,
                "offset": offset,
            }
        )
        return self._get(f"{self.base_url}/loops", params=params)

    def get_loops_me(self):
        return self._get(f"{self.base_url}/loops/me")

    def get_package(self, id: str = ""):
        return self._get(f"{self.base_url}/packages/{id}")

    def get_packages(
        self,
        tracking_number: str | None = None,
        loop_id: PydanticObjectId | None = None,
        limit: int = 999,
        offset: int = 0,
    ):
        params = remove_empties_from_dict(
            {
                "tracking_number": tracking_number,
                "loop_id": loop_id,
                "limit": limit,
                "offset": offset,
            }
        )
        return self._get(f"{self.base_url}/packages", params=params)

    def create_package(self, body: Dict[str, Any]):
        return self._post(f"{self.base_url}/packages", json=body)

    def delete_package(self, id: PydanticObjectId):
        return self._delete(f"{self.base_url}/packages/{id}")

    def get_sessions(self, loop_id: PydanticObjectId):
        return self._get(f"{self.base_url}/loops/{loop_id}/sessions")

    async def listen_status(self, loop_id: PydanticObjectId, process_fn=print):
        uri = f"wss://{self.base_url.lstrip('https://')}/loops/{loop_id}/status?token={self.token}"
        async with connect(uri) as ws:
            # Close the connection when receiving SIGTERM, SIGINT
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, loop.create_task, ws.close())
            loop.add_signal_handler(signal.SIGINT, loop.create_task, ws.close())

            # Process messages received on the connection.
            async for message in ws:
                process_fn(message)

    async def listen_data(
        self,
        loop_id: PydanticObjectId,
        *,
        type="eeg",
        process_fn=print,
    ):
        uri = f"wss://{self.base_url.lstrip('https://')}/loops/{loop_id}/data?type={type}&token={self.token}"
        async with connect(uri) as ws:
            # Close the connection when receiving SIGTERM, SIGINT
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, loop.create_task, ws.close())
            loop.add_signal_handler(signal.SIGINT, loop.create_task, ws.close())

            # Process messages received on the connection.
            async for message in ws:
                process_fn(message)
