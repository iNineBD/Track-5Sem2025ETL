"""
Module for authentication with Taiga API.
"""

import os
import requests
from dotenv import load_dotenv
from taiga import TaigaAPI

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
    # Initialize the Taiga API client
    api = TaigaAPI()
    api.auth(
        username=TAIGA_USER,
        password=TAIGA_PASSWORD
    )
    token = api.token
    return token