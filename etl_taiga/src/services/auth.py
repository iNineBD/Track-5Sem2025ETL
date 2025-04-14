"""
Module for authentication with Taiga API.
"""

import os
import requests
from dotenv import load_dotenv

# %%

load_dotenv()

TAIGA_HOST = os.getenv("TAIGA_HOST")
TAIGA_USER = os.getenv("TAIGA_USER")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD")


# %%
def auth_taiga():
    """
    Authenticate with Taiga and return the token.
    """
    auth_user = {"type": "normal", "username": TAIGA_USER, "password": TAIGA_PASSWORD}
    auth_response = requests.post(f"{TAIGA_HOST}/auth", json=auth_user, timeout=10)

    if auth_response.status_code == 200:
        return auth_response.json()["auth_token"]
    else:
        raise Exception(
            f"Erro na autenticação: {auth_response.status_code} - {auth_response.text}"
        )
