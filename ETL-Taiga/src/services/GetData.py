# %%
import requests
import json
import pandas as pd
from src.services.Auth import auth_taiga
from taiga import TaigaAPI
# %%
taiga_host = 'http://209.38.145.133:9000/'
taiga_user = 'taiga-admin'
taiga_password = 'admin'
token = auth_taiga()
# %%
url = f"{taiga_host}/api/v1"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {token}"
}

def fetch_data(endpoint):
    """faz a requisição get para a api do taiga e retorna o json"""
    response = requests.get(f"{url}/{endpoint}", headers=headers)
    if response.status_code == 200:
        try:
            data  = response.json()
            return data if isinstance(data, list) else data['data']
        except requests.exceptions:
            return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"
    else:
        return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"