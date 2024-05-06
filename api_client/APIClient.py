import os
import asyncio
import signal
from typing import Any
import httpx
from websockets.client import connect

from .schemas.pydanticobjectid import PydanticObjectId


class APIClient:
    def __init__(
        self,
        base_url: str = os.environ.get("API_BASE_URL", "https://dev.tempzeit.com"),
        username: str | None = None,
        password: str | None = None,
        access_token: str | None = None,
        headers: dict | None = None,
    ):
        if headers is None:
            headers = {}
        self.access_token = access_token
        if access_token:
            headers = {"Authorization": f"Bearer {self.access_token}"}
        self.client = httpx.Client(base_url=base_url, headers=headers)
        if username and password:
            self.auth(username, password)

    def login(self, username: str, password: str):
        return self.auth(username, password)

    def logout(self):
        return self.client.post("/auth/logout")

    def auth(self, username: str, password: str):
        if self.access_token:
            return True
        res = self.client.post(
            "/auth/login",
            data={
                "username": username,
                "password": password,
            },
        )
        if res.status_code == 200:
            self.access_token = res.json().get("access_token", "")
            self.client.headers.update({"Authorization": f"Bearer {self.access_token}"})
            return True
        else:
            return False

    def get_me(self):
        res = self.client.get("/users/me")
        if res.status_code == 200:
            return res.json()
        else:
            raise RuntimeError(f"Invalid status code {res.status_code}")

    def register_user(self, body):
        return self.client.post("/auth/register", json=body)

    def request_verify_token(self, email: str):
        return self.client.post("/auth/request-verify-token", json={"email": email})

    def get_user(self, id: PydanticObjectId):
        return self.client.get(f"/users/{id}")

    def get_user_loops(self, id: PydanticObjectId):
        return self.client.get(f"users/{id}/loops")

    def get_users(
        self,
        email: str | None = None,
        loop_id: PydanticObjectId | None = None,
        limit: int = 100,
        offset: int = 0,
    ):
        _params = {
            "loop_id": loop_id,
            "limit": limit,
            "offset": offset,
            "email": email,
        }
        params = {k: v for k, v in _params.items() if v}
        res = self.client.get("/users", params=params)

        if res.status_code != 200:
            raise RuntimeError(f"Invalid status code {res.status_code}")
        return res.json()["items"]

    def patch_user(self, id: PydanticObjectId, body: dict[str, Any]):
        return self.client.patch(f"/users/{id}", json=body)

    def delete_user(self, id: str):
        return self.client.delete(f"/users/{id}")

    def create_loop(self, body: dict[str, Any]):
        return self.client.post("/loops", json=body)

    def patch_loop(self, id: PydanticObjectId, body: dict[str, Any]):
        return self.client.patch(f"/loops/{id}", json=body)

    def delete_loop(self, id: PydanticObjectId):
        return self.client.delete(f"/loops/{id}")

    def get_loop(self, id: PydanticObjectId):
        return self.client.get(f"/loops/{id}")

    def get_loops(
        self,
        name: str | None = None,
        status: str | None = None,
        type_: str | None = None,
        limit: int = 999,
        offset: int = 0,
    ):
        _params = {
            "name": name,
            "limit": limit,
            "status": status,
            "type": type_,
            "offset": offset,
        }
        params = {k: v for k, v in _params.items() if v}
        res = self.client.get("/loops", params=params)
        if res.status_code != 200:
            raise RuntimeError(f"Invalid status code {res.status_code}")
        return res.json()["items"]

    def get_loops_me(self):
        return self.client.get("/loops/me")

    def get_package(self, id: str):
        return self.client.get(f"/packages/{id}")

    def get_packages(
        self,
        tracking_number: str | None = None,
        loop_id: PydanticObjectId | None = None,
        limit: int = 999,
        offset: int = 0,
    ):
        _params = {
            "tracking_number": tracking_number,
            "loop_id": loop_id,
            "limit": limit,
            "offset": offset,
        }
        params = {k: v for k, v in _params.items() if v}
        return self.client.get("/packages", params=params)

    def create_package(self, body: dict[str, Any]):
        return self.client.post("/packages", json=body)

    def delete_package(self, id: PydanticObjectId):
        return self.client.delete(f"/packages/{id}")

    def get_sessions(self, loop_id: PydanticObjectId):
        return self.client.get(f"/loops/{loop_id}/sessions")

    async def listen_status(self, loop_id: PydanticObjectId, process_fn=print):
        uri = f"wss://{str(self.client.base_url).lstrip('https://')}/loops/{loop_id}/status?token={self.access_token}"
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
        uri = f"wss://{str(self.client.base_url).lstrip('https://')}/loops/{loop_id}/data?type={type}&token={self.access_token}"
        async with connect(uri) as ws:
            # Close the connection when receiving SIGTERM, SIGINT
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signal.SIGTERM, loop.create_task, ws.close())
            loop.add_signal_handler(signal.SIGINT, loop.create_task, ws.close())

            # Process messages received on the connection.
            async for message in ws:
                process_fn(message)
