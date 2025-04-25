# src/services/auth.py
"""
Module for authentication with Taiga API.
"""
import os
from dotenv import load_dotenv
import requests

# Carregar variáveis do .env
# URL e credenciais do Taiga
from ..config import TAIGA_HOST, TAIGA_USER, TAIGA_PASSWORD


def auth_taiga():
    """
    Authenticate with Taiga and return the token.
    Raises an Exception if authentication fails.
    """
    auth_user = {
        "type": "normal",
        "username": TAIGA_USER,
        "password": TAIGA_PASSWORD,
    }

    try:
        response = requests.post(
            f"{TAIGA_HOST}/api/v1/auth", json=auth_user, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        token = data.get("auth_token")

        if not token:
            raise Exception("Auth token not found in response")

        return token

    except requests.RequestException as e:
        raise Exception(f"Erro de conexão com Taiga: {e}")
    except Exception as e:
        raise Exception(f"Erro ao autenticar com Taiga: {e}")
