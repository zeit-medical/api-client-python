
from api_client import APIClient


class TestRoutes:
    username = "admin@zeitmedical.com"
    password =  "oG9!YvYSho2VC!"
    def test_login_routes_password(self):
        client = APIClient()
        client.login(self.username, self.password)
        client.logout()

    def test_login_routes_token(self):
        client = APIClient(token="c4c12c4e-c786-49db-913d-89df9918bebc")
        client.get_loops()


    def test_auth_routes(self):
        client = APIClient(username=self.username, password=self.password)
        client.get_loops()


    def test_loop_routes(self):
        client = APIClient(username=self.username, password=self.password)
        client.get_loops()





        
