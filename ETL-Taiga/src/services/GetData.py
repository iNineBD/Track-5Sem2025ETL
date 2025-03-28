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

# %%

def pipeline_projets():
    """pipeline para gerar dataframes de projetos"""
    projects = fetch_data("projects")
    # selecionando apenas os projetos que são da empresa
    campos = ['id', 'name', 'description', 'created_date', 'modified_date']
    projects = pd.DataFrame(projects)[campos]
    return projects

def pipeline_users():
    """pipeline para gerar dataframes de users"""
    users = fetch_data("users")
    campos = ['id','full_name_display','color']

    list_roles = []
    for user in users:
        user_id = user.get("id")
        roles = user.get("roles", [])

        if isinstance(roles, list):
            for role in roles:
                if isinstance(role, dict):
                    role_copy = role.copy()
                    role_copy["user_id"] = user_id
                    list_roles.append(role_copy)
                else:
                    list_roles.append({"user_id": user_id,"role_name": role})

    users = pd.DataFrame(users)[campos]
    roles = pd.DataFrame(list_roles) if list_roles else None

    return users, roles

# Executando a pipeline
df_projects = pipeline_projets()
df_users,df_roles = pipeline_users()