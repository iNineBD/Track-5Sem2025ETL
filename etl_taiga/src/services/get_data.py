"""
Module for data extraction and transformation.
"""

import os
import numpy as np
import pandas as pd
import requests
from etl_taiga.src.services.auth import auth_taiga
from dotenv import load_dotenv
import gc

load_dotenv()

TAIGA_HOST = os.getenv("TAIGA_HOST")
TAIGA_USER = os.getenv("TAIGA_USER")
TAIGA_PASSWORD = os.getenv("TAIGA_PASSWORD")
TAIGA_MEMBER = os.getenv("TAIGA_MEMBER")
TOKEN = auth_taiga()

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {TOKEN}"}


def pipeline_projets():
    """
    Generate a DataFrame for projects.
    """
    url_projects = f"{TAIGA_HOST}/projects?member={TAIGA_MEMBER}"

    response = requests.get(url_projects, headers=headers, timeout=10)
    response.raise_for_status()

    projects = response.json()
    campos = ["id", "name", "description"]  # inclua 'id' aqui
    df_projects = pd.DataFrame(projects)[campos].reset_index(drop=True)

    df_projects.rename(
        columns={"id": "id_project", "name": "name_project"}, inplace=True
    )
    ids_projects = df_projects["id_project"].tolist()
    return df_projects, ids_projects


def pipeline_cards(id_projects):
    """
    Generate a DataFrame for cards.
    """
    url_cards = f"{TAIGA_HOST}/userstories?project="

    id_cards = []
    df_cards = pd.DataFrame(
        columns=[
            "id",
            "assigned_to",
            "tags",
            "subject",
            "description",
            "created_date",
            "status",
            "project",
        ]
    )
    df_users = pd.DataFrame(columns=["id", "name", "email", "password", "id_role"])
    df_status = pd.DataFrame(columns=["status"])
    df_tags = pd.DataFrame(columns=["tags", "id"])
    df_status = pd.DataFrame(columns=["id_status", "name_status"])

    tag_map = {}
    next_tag_id = 1

    for project_id in id_projects:
        # Obter cards do projeto
        response = requests.get(f"{url_cards}{project_id}", headers=headers, timeout=10)
        response.raise_for_status()
        cards = response.json()

        for card in cards:
            # Extrair o ID do card
            card_id = card.get("id")
            if card_id:
                id_cards.append(card_id)

            tags = card.get("tags") or [None]

            for tag in tags:
                tag_value = tag[0] if isinstance(tag, list) and tag else None

                tag_id = None
                if tag_value:
                    if tag_value not in tag_map:
                        tag_map[tag_value] = next_tag_id
                        next_tag_id += 1
                    tag_id = tag_map[tag_value]

                name_status = card.get("status_extra_info")
                # Extrair informações para df_cards
                df_cards = pd.concat(
                    [
                        df_cards,
                        pd.DataFrame(
                            [
                                {
                                    "id": card_id,
                                    "assigned_to": card.get("assigned_to"),
                                    "tags": tag_value,
                                    "subject": card.get("subject"),
                                    "description": card.get("description"),
                                    "created_date": card.get("created_date"),
                                    "status": name_status.get("name"),
                                    "project": project_id,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

                # Extrair informações para df_tags
                df_status = pd.concat(
                    [
                        df_status,
                        pd.DataFrame(
                            [
                                {
                                    "id_status": card.get("status"),
                                    "name_status": name_status.get("name"),
                                }
                            ]
                        ),
                    ],
                )

                df_tags = pd.concat(
                    [df_tags, pd.DataFrame([{"tags": tag_value, "id": tag_id}])],
                    ignore_index=True,
                )

            # Extrair informações para df_users, tratando o caso onde 'assigned_to' é um ID (inteiro)
            assigned_to = card.get("assigned_to")
            assigned_to_extra_info = card.get("assigned_to_extra_info")

            if assigned_to is not None and isinstance(assigned_to_extra_info, dict):
                df_users = pd.concat(
                    [
                        df_users,
                        pd.DataFrame(
                            [
                                {
                                    "id": assigned_to,
                                    "name": assigned_to_extra_info.get(
                                        "full_name_display"
                                    ),
                                    "email": assigned_to_extra_info.get("email"),
                                    "password": None,
                                    "id_role": None,
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

            if card.get("status"):
                df_status = pd.concat(
                    [df_status, pd.DataFrame([{"status": card["status"]}])],
                    ignore_index=True,
                )

    df_cards.drop_duplicates(inplace=True)
    df_users.drop_duplicates(inplace=True)
    # df_status.drop_duplicates(inplace=True)
    df_tags.drop_duplicates(inplace=True)
    df_tags.dropna(inplace=True)

    url_status = f"{TAIGA_HOST}/userstory-statuses"
    list_status = df_status["status"].tolist()

    # nova coluna name para df_status
    df_status["name"] = None

    for status in list_status:
        response = requests.get(f"{url_status}/{status}", headers=headers, timeout=10)
        response.raise_for_status()
        resp_status = response.json()
        # adicionar o nome do status
        df_status.loc[df_status["status"] == status, "name"] = resp_status.get("name")
    df_status = df_status.drop_duplicates(subset="name_status").reset_index(drop=True)

    # extrair description de cards
    url_cards_full = f"{TAIGA_HOST}/userstories/"
    list_ids_cards = df_cards["id"].tolist()

    for id_card in list_ids_cards:
        response = requests.get(
            f"{url_cards_full}{id_card}", headers=headers, timeout=10
        )
        response.raise_for_status()
        cards = response.json()

        # adicionar a description
        df_cards.loc[df_cards["id"] == id_card, "description"] = cards.get(
            "description"
        )

    # pegar roles e email dos users
    url_users = f"{TAIGA_HOST}/memberships?project="
    df_roles = pd.DataFrame(columns=["id", "name"])
    for id_project in id_projects:
        response = requests.get(f"{url_users}{id_project}", headers=headers, timeout=10)
        response.raise_for_status()
        users = response.json()

        for user in users:
            user_id = user.get("user")
            user_email = user.get("user_email")
            role_id = user.get("role")
            role_name = user.get("role_name")

            if user_id and user_email:
                df_users.loc[df_users["id"] == user_id, "email"] = user_email
                df_users.loc[df_users["id"] == user_id, "id_role"] = role_id
                df_roles = pd.concat(
                    [df_roles, pd.DataFrame([{"id": role_id, "name": role_name}])],
                    ignore_index=True,
                )

    tag_map = dict(zip(df_tags["tags"], df_tags["id"]))
    df_cards["tags"] = df_cards["tags"].map(tag_map)
    # convertir tags para int
    df_cards["tags"] = df_cards["tags"].fillna(0).astype(int)

    return df_cards, df_users, df_tags, df_status


def pipeline_transform(df_cards, df_users, df_tags, df_status):
    """
    Transform the data for the ETL pipeline.
    """
    # Transformar os dados para o formato desejado

    # dataframes para tempo
    df_cards["created_date"] = pd.to_datetime(df_cards["created_date"], utc=True)
    df_time = pd.DataFrame()
    df_time["id_time"] = range(1, len(df_cards) + 1)
    df_time["id_year"] = df_cards["created_date"].dt.year
    df_time["id_month"] = df_cards["created_date"].dt.month
    df_time["id_day"] = df_cards["created_date"].dt.day
    df_time["id_hour"] = df_cards["created_date"].dt.hour
    df_time["id_minute"] = df_cards["created_date"].dt.minute
    df_time = df_time[["id_time", "id_day", "id_month", "id_year", "id_hour", "id_minute"]]

    # df para usuarios


    return df_time


def pipeline_main():
    """
    Main function to run the ETL pipeline.
    """

    df_projects, ids_projects = pipeline_projets()
    df_cards, df_status, df_tags, id_users, df_time = pipeline_cards(ids_projects)
    df_users, df_roles = pipeline_users(ids_projects)

    # Dimensão Year
    df_year = df_time[["year"]].drop_duplicates().reset_index(drop=True)
    df_year["id_year"] = df_year.index + 1
    # Dimensão Month
    df_month = df_time[["month"]].drop_duplicates().reset_index(drop=True)
    df_month["id_month"] = df_month.index + 1
    # Dimensão Day
    df_day = df_time[["day"]].drop_duplicates().reset_index(drop=True)
    df_day["id_day"] = df_day.index + 1
    # Dimensão Hour
    df_hour = df_time[["hour"]].drop_duplicates().reset_index(drop=True)
    df_hour["id_hour"] = df_hour.index + 1
    # Dimensão Minute
    df_minute = df_time[["minute"]].drop_duplicates().reset_index(drop=True)
    df_minute["id_minute"] = df_minute.index + 1

    dim_time = df_time.copy()

    dim_time = dim_time.merge(df_year, on="year", how="left")
    dim_time = dim_time.merge(df_month, on="month", how="left")
    dim_time = dim_time.merge(df_day, on="day", how="left")
    dim_time = dim_time.merge(df_hour, on="hour", how="left")
    dim_time = dim_time.merge(df_minute, on="minute", how="left")

    # Selecionar apenas os ids das dimensões + o id original
    dim_time = dim_time[["id", "id_year", "id_month", "id_day", "id_hour", "id_minute"]]

    fato_cards = pd.DataFrame()
    fato_cards["id"] = range(1, len(df_cards) + 1)
    fato_cards["id_card"] = df_cards["id_card"]
    fato_cards["id_project"] = df_cards["project"]
    fato_cards["id_user"] = df_users["id_user"]
    fato_cards["id_status"] = df_status["id_status"]
    fato_cards["id_tag"] = df_tags["id_tag"]
    fato_cards["qtd_cards"] = 1

    df_cards = df_cards.drop(columns=["project", "fk_id_user", "id_tag"])

    return (
        fato_cards,
        df_projects,
        df_cards,
        df_status,
        df_tags,
        df_users,
        df_roles,
        dim_time,
        df_year,
        df_month,
        df_day,
        df_hour,
        df_minute,
    )


# %%

(
    fato_cards,
    df_projects,
    df_cards,
    df_status,
    df_tags,
    df_users,
    df_roles,
    dim_time,
    df_year,
    df_month,
    df_day,
    df_hour,
    df_minute,
) = pipeline_main()
