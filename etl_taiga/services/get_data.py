# src/services/get_data.py
"""
Module for data extraction and transformation.
"""
import requests
import pandas as pd

from ..config import TAIGA_HOST
from etl_taiga.services.auth import auth_taiga

_TOKEN = None


def get_token():
    global _TOKEN
    if _TOKEN is None:
        _TOKEN = auth_taiga()
    return _TOKEN


def fetch_data(endpoint):
    """
    Fetch data from the Taiga API.
    """
    global TOKEN
    if not TOKEN:
        TOKEN = auth_taiga()  # Lazy-load the token the first time it's needed

    url = f"{TAIGA_HOST}/api/v1"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token()}",
    }

    response = requests.get(f"{url}/{endpoint}", headers=headers, timeout=10)
    if response.status_code == 200:
        try:
            data = response.json()
            return data if isinstance(data, list) else data["data"]
        except Exception:
            return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"
    else:
        return f"Erro ao fazer a requisição: {response.status_code} - {response.text}"


def pipeline_projets():
    """
    Generate a DataFrame for projects.
    """
    projects = fetch_data("projects")
    campos = ["id", "name", "description", "created_date", "modified_date"]
    projects = pd.DataFrame(projects)[campos].reset_index(drop=True)
    return projects


def pipeline_roles():
    """
    Generate a DataFrame for roles.
    """
    roles = fetch_data("roles")
    campos = ["id", "name"]
    roles = pd.DataFrame(roles)[campos]
    roles = roles.drop_duplicates(subset=["name"], keep="first").reset_index(drop=True)
    roles["id"] = roles.index + 1
    return roles


def pipeline_users(roles):
    """
    Generate a DataFrame for users with foreign key to roles.
    """
    users = fetch_data("users")
    campos = ["id", "full_name_display", "color"]

    df_users_input = pd.DataFrame(users)[campos]

    # role_map = dict(zip(roles["name"], roles["id"]))
    #
    # user_role_map = {}
    #
    # for user in users:
    #     user_id = user["id"]
    #     user_roles = user.get("roles", [])
    #
    #     for role_name in user_roles:
    #         if role_name in role_map:
    #             user_role_map[user_id] = role_map[role_name]
    #             break

    df_users_input["fk_id_role"] = df_users_input.index + 1
    df_users_input = df_users_input.rename(columns={"full_name_display": "full_name"})
    return df_users_input


def pipeline_tags():
    """
    Generate a DataFrame for tags.
    """
    user_stories = fetch_data("userstories")
    campos = ["id", "tags", "project"]

    tags = pd.DataFrame(user_stories)[campos]
    tags = tags.explode("tags").reset_index(drop=True)
    tags[["name", "color"]] = tags["tags"].apply(pd.Series)
    tags = tags.drop(columns=["tags"])
    tags = tags.rename(columns={"id": "id_card", "project": "id_project"})
    tags.loc[tags["name"].notna() & tags["color"].isna(), "color"] = "#a9aabc"
    tags.dropna(inplace=True)
    tags["color"] = tags["color"].str.upper()
    tags = tags.reset_index(drop=True)
    tags["id"] = tags.index + 1
    return tags


def pipeline_status():
    """
    Generate a DataFrame for status.
    """
    status = fetch_data("userstories")
    campos = ["id", "status_extra_info", "project"]

    status = pd.DataFrame(status)[campos]
    status["name"] = status["status_extra_info"].apply(lambda x: x["name"])
    status = status.drop(columns=["status_extra_info"])
    status = status.rename(columns={"id": "id_card", "project": "id_project"})
    status["id"] = status.index + 1
    return status


def pipeline_fact_cards():
    """
    Gera um DataFrame para os fact cards, fazendo os merges estáveis com status, tags e outros dados necessários.
    """
    # Etapa 1: Obter os dados de tags, status e userstories
    tags = pipeline_tags()  # Dados sobre as tags
    status = pipeline_status()  # Dados sobre o status
    cards = fetch_data("userstories")  # Dados dos cards

    # Etapa 2: Preparação inicial dos dados de userstories
    df_cards = pd.DataFrame(cards)[["project", "assigned_to"]]
    df_cards = df_cards.rename(columns={"assigned_to": "fk_id_user", "project": "fk_id_project"})

    # Etapa 3: Adicionar quantidade de cards (qtd_card)
    # Vamos assumir que a quantidade inicial de cards é 1 (você pode modificar isso se necessário)
    df_cards["qtd_card"] = 1

    # Etapa 4: Merge com as tags (relacionamento de id_tag)
    df_tags = tags[["id", "id_project"]]
    df_cards = df_cards.merge(df_tags, how="left", left_on="fk_id_project", right_on="id")
    df_cards["fk_id_tag"] = df_cards["id"]
    df_cards.drop(columns=["id"], inplace=True)

    # Etapa 5: Merge com o status (relacionamento de id_status)
    df_status = status[["id", "id_project"]]
    df_cards = df_cards.merge(df_status, how="left", left_on="fk_id_project", right_on="id")
    df_cards["fk_id_status"] = df_cards["id"]
    df_cards.drop(columns=["id"], inplace=True)

    # Etapa 6: Garantir que as colunas estão corretas e ajustar a estrutura
    df_cards = df_cards[["fk_id_status", "fk_id_tag", "fk_id_user", "fk_id_project", "qtd_card"]]

    # Etapa 7: Ajustar tipos das colunas
    df_cards = df_cards.astype(int)

    return df_cards
