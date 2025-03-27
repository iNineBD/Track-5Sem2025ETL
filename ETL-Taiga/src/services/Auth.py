import requests

# %%

taiga_host = 'http://209.38.145.133:9000/'
taiga_user = 'taiga-admin'
taiga_password = 'admin'

# %%

"""authenticates with taiga and returns the api object"""
def auth_taiga():
    auth_user = {"type": "normal", "username": taiga_user, "password": taiga_password}
    auth_response = requests.post(f"{taiga_host}/api/v1/auth", json=auth_user)
    token = auth_response.json()['auth_token']
    return token