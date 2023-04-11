
from api_client import APIClient


class TestRoutes:
    username = "TODO"
    password =  "TODO"
    def test_login_routes_password(self):
        client = APIClient()
        client.login(self.username, self.password)
        client.logout()

    def test_login_routes_token(self):
        client = APIClient(token="TODO")
        client.get_loops()


    def test_auth_routes(self):
        client = APIClient(username=self.username, password=self.password)
        client.get_loops()


    def test_loop_routes(self):
        client = APIClient(username=self.username, password=self.password)
        client.get_loops()





        
