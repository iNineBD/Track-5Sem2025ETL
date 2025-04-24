"""
Module for authentication with Taiga API.
"""

import requests

TAIGA_HOST = "http://209.38.145.133:9000/"
TAIGA_USER = "taiga-admin"
TAIGA_PASSWORD = "admin"


def auth_taiga():
    """
    Authenticate with Taiga and return the token.
    """
    auth_user = {"type": "normal", "username": TAIGA_USER, "password": TAIGA_PASSWORD}
    auth_response = requests.post(f"{TAIGA_HOST}/api/v1/auth", json=auth_user, timeout=10)
#   auth_response = requests.post(f"{TAIGA_HOST.rstrip('/')}/api/v1/auth", json=auth_user, timeout=10) - melhora a f-string,URL final sempre vai estar correta, com só uma /
    token = auth_response.json()["auth_token"]
    return token
