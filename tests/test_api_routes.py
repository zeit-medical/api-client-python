import os
from uuid import uuid4
from api_client import APIClient
import pytest


@pytest.fixture
def client():
    return APIClient(
        username=os.environ["API_USERNAME"], password=os.environ["API_PASSWORD"]
    )


@pytest.fixture
def body():
    return {
        "password": "userpassword1#",
        "email": "test@test.com",
        "is_active": True,
        "is_superuser": False,
        "is_verified": True,
        "short_name": "Gerrit",
        "full_name": "",
        "patient_code": "",
        "site_code": "",
        "address": {
            "street_address": "Johnson Street 992",
            "city": "San Francisco ",
            "country_area": "CA",
            "postal_code": "94061",
            "country_code": "US",
        },
        # This is a special Twilio number that will pass all validation:
        "phone": "+15005550006",
        "role": "patient",
        "timezone": "America/Los_Angeles",
        "enroller_email": "enroller@foo.com",
    }


@pytest.fixture
def test_user(request, client, body):
    def teardown():
        user = client.get_users(email="test@test.com")
        client.delete_user(user["items"][0]["_id"])

    request.addfinalizer(teardown)

    yield client.register_user(body)


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
        client.delete_loop(res["_id"])
        client.get_loops_me()

    def test_register_user(self, client, test_user):
        pass
