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

_,ids_projects = pipeline_projets()


def pipeline_cards(id_projects):
    """
    Generate a DataFrame for cards.
    """
    id_cards = []
    # coletar os ids das users stories por projeto
    for (project_id) in id_projects:
        response = requests.get(f"{url_cards}{project_id}", headers=headers, timeout=10)
        response.raise_for_status()
        cards = pd.DataFrame(response.json())
        id_cards.append(cards["id"].tolist())

    # unir os ids das users stories
    id_cards = list(np.concatenate(id_cards))

    df_cards = pd.DataFrame(columns=["project", "assigned_to", "subject", "tags", "description", "created_date", "status"])

    for card_id in id_cards:
        response = requests.get(f"{url_cards_full}{card_id}", headers=headers, timeout=10)
        response.raise_for_status()
        card_data = response.json()

        filtered_data = {campo: card_data.get(campo, None) for campo in df_cards.columns}
        df_temp = pd.DataFrame([filtered_data])

        if not df_temp.empty:
            df_cards = pd.concat([df_cards, df_temp], ignore_index=True)

    return df_cards


# %%
df_projects = pipeline_projets()
df_roles = pipeline_roles()
df_users = pipeline_users(df_roles)
df_tags = pipeline_tags()
df_status = pipeline_status()
df_fact_cards = pipeline_fact_cards()
