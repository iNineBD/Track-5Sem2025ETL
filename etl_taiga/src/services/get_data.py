"""
Module for data extraction and transformation.
"""

import os
import numpy as np
import pandas as pd
import requests
from etl_taiga.src.services.auth import auth_taiga
from dotenv import load_dotenv

# %%

load_dotenv()

TAIGA_HOST = os.getenv("TAIGA_HOST")
TAIGA_USER = os.getenv("TAIGA_USER")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD")
TAIGA_MEMBER = os.getenv("TAIGA_MEMBER")
TOKEN = auth_taiga()

headers = {"Content-Type": "application/json","Authorization": f"Bearer {TOKEN}"}
url_projects = f"{TAIGA_HOST}/projects?member={TAIGA_MEMBER}"
url_roles = f"{TAIGA_HOST}/roles?project="
url_cards = f"{TAIGA_HOST}/userstories?project="
url_cards_full = f"{TAIGA_HOST}/userstories/"

# %%
def pipeline_projets():
    """
    Generate a DataFrame for projects.
    """
    def fetch_data_projects():
        response = requests.get(url_projects, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()

    projects = fetch_data_projects()
    campos = ["id", "name", "description"]
    df_projects = pd.DataFrame(projects)[campos].reset_index(drop=True)
    df_projects.rename(
        columns={
            "id": "id_project",
            "name": "project_name",
            "description": "description",
        }
    )
    ids_projects = df_projects["id"].tolist()
    return df_projects, ids_projects


# %%
def pipeline_cards(id_projects):
    """
    Generate a DataFrame for cards.
    """
    url_status = f"{TAIGA_HOST}/userstory-statuses"
    id_cards = []
    # coletar os ids das users stories por projeto
    url_cards = f"{TAIGA_HOST}/userstories?project="
    for project_id in id_projects:
        response = requests.get(f"{url_cards}{project_id}", headers=headers, timeout=10)
        response.raise_for_status()
        cards = pd.DataFrame(response.json())
        id_cards.append(cards["id"].tolist())

    # unir os ids das users stories
    id_cards = list(np.concatenate(id_cards))

    df_cards = pd.DataFrame(
        columns=[
            "id",
            "assigned_to",
            "subject",
            "tags",
            "description",
            "created_date",
            "status",
        ]
    )
    url_cards_full = f"{TAIGA_HOST}/userstories/"
    # coletar os dados filtrados das users stories
    for card_id in id_cards:
        response = requests.get(
            f"{url_cards_full}{card_id}", headers=headers, timeout=10
        )
        response.raise_for_status()
        cards = response.json()

        # filtrar os dados
        filtered_data = {campo: cards.get(campo, None) for campo in df_cards.columns}
        df_temp = pd.DataFrame([filtered_data])
        # adiciona os dados filtrados ao DataFrame se nao estiver vazio
        if not df_temp.empty:
            df_cards = pd.concat([df_cards, df_temp], ignore_index=True)

    id_status = df_cards["status"].tolist()
    df_status = pd.DataFrame(columns=["id", "name"])
    # coletar os status das users stories
    for status_id in id_status:
        response = requests.get(
            f"{url_status}/{status_id}", headers=headers, timeout=10
        )
        response.raise_for_status()
        status = response.json()

        # filtrar os dados
        filtered_data = {campo: status.get(campo, None) for campo in df_status.columns}
        df_temp = pd.DataFrame([filtered_data])
        # adiciona os dados filtrados ao DataFrame se nao estiver vazio
        if not df_temp.empty:
            df_status = pd.concat([df_status, df_temp], ignore_index=True)

    # coletrar as tags
    df_tags = pd.DataFrame()
    df_tags["name"] = df_cards["tags"].apply(lambda lista: [item[0] for item in lista])
    df_tags["id"] = df_tags.index + 1

    # id tag para df_cards
    df_cards["id_tag"] = df_tags["id"]

    df_cards = df_cards.rename(
        columns={
            "subject": "name",
            "status": "fk_id_status",
            "assigned_to": "fk_id_user",
        }
    ).drop(columns=["tags"])
    df_cards["created_date"] = pd.to_datetime(df_cards["created_date"], utc=True)
    df_time = pd.DataFrame()
    df_time["id"] = range(1, len(df_cards) + 1)
    df_time["year"] = df_cards["created_date"].dt.year
    df_time["month"] = df_cards["created_date"].dt.month
    df_time["day"] = df_cards["created_date"].dt.day
    df_time["hour"] = df_cards["created_date"].dt.hour
    df_time["minute"] = df_cards["created_date"].dt.minute
    df_time = df_time[["id", "year", "month", "day", "hour", "minute"]]

    # dropar coluna data
    df_cards = df_cards.drop(columns=["created_date"])

    id_users = df_cards["fk_id_user"].unique().tolist()

    # limpar variaveis
    del id_cards
    del cards
    del df_temp
    gc.collect()

    return df_cards, df_status, df_tags, id_users, df_time


# %%
df_projects = pipeline_projets()
df_roles = pipeline_roles()
df_users = pipeline_users(df_roles)
df_tags = pipeline_tags()
df_status = pipeline_status()
df_fact_cards = pipeline_fact_cards()
