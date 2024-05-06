import os
from uuid import uuid4
from api_client import APIClient


class TestRoutes:
    username = os.environ["API_USERNAME"]
    password = os.environ["API_PASSWORD"]

    def test_login_routes_password(self):
        client = APIClient()
        client.login(self.username, self.password)
        client.auth(self.username, self.password)
        client.logout()

    def test_login_routes_token(self):
        client = APIClient(access_token=os.environ["AUTH_TOKEN"])
        client.get_loops()

    def test_loop_routes(self):
        client = APIClient(username=self.username, password=self.password)
        client.get_loops()
        res = client.create_loop(
            body={
                "name": "test" + str(uuid4()),
                "type": "pi4",
                "status": "created",
            }
        )
        client.delete_loop(res.json()["_id"])
        client.get_loops_me()
