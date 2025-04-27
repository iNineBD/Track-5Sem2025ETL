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


def pipeline_projects():
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
    df_users = pd.DataFrame(columns=["id", "name", "email", "password", "name_role"])
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
                                }
                            ]
                        ),
                    ],
                    ignore_index=True,
                )

    df_cards = df_cards.drop_duplicates().reset_index(drop=True)
    df_users = df_users.drop_duplicates().reset_index(drop=True)
    df_tags = df_tags.drop_duplicates().dropna().reset_index(drop=True)
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
                df_users.loc[df_users["id"] == user_id, "name_role"] = role_name
                df_roles = pd.concat(
                    [df_roles, pd.DataFrame([{"id": role_id, "name": role_name}])],
                    ignore_index=True,
                )

    tag_map = dict(zip(df_tags["tags"], df_tags["id"]))
    df_cards["tags"] = df_cards["tags"].map(tag_map)
    # convertir tags para int
    df_cards["tags"] = df_cards["tags"].fillna(pd.NA).astype("Int64")
    df_roles = df_roles.drop_duplicates(subset="name").reset_index(drop=True)

    # renomeando as colunas
    df_tags = df_tags.rename(columns={"tags": "tag_name", "id": "id_tag"})
    df_tags = df_tags[["id_tag", "tag_name"]]
    df_cards = df_cards.rename(
        columns={
            "project": "id_project",
            "assigned_to": "id_user",
            "tags": "id_tag",
            "id": "id_card",
            "subject": "name_card",
            "status": "id_status",
        }
    )
    df_roles = df_roles.rename(columns={"id": "id_role", "name": "name_role"})
    df_users = df_users.rename(columns={"id": "id_user", "name": "name_user"})
    df_cards["created_date"] = pd.to_datetime(df_cards["created_date"], dayfirst=True)

    # garbage collection
    del card
    del cards
    del assigned_to
    del assigned_to_extra_info
    del card_id
    del id_card
    del id_cards
    del id_project
    del id_projects
    del list_ids_cards
    del next_tag_id
    del project_id
    del response
    del role_id
    del role_name
    del tag
    del tag_id
    del tag_map
    del tag_value
    del tags
    del url_cards
    del url_cards_full
    del url_users
    del user
    del user_email
    del user_id
    del users
    gc.collect()

    return df_cards, df_users, df_tags, df_status, df_roles


def pipeline_transform(df_cards, df_status, df_users, df_roles):
    """
    Transform the data for the ETL pipeline.
    """
    # Transformar os dados para o formato desejado

    # dataframes para tempo
    # extrair tempo
    df_cards["day"] = df_cards["created_date"].dt.day
    df_cards["month"] = df_cards["created_date"].dt.month
    df_cards["year"] = df_cards["created_date"].dt.year
    df_cards["hour"] = df_cards["created_date"].dt.hour
    df_cards["minute"] = df_cards["created_date"].dt.minute

    def create_dim(df, column, id_name):
        dim = (
            pd.DataFrame({column: df[column].unique()})
            .sort_values(column)
            .reset_index(drop=True)
        )
        dim[id_name] = dim.index + 1
        return dim

    # criar tabelas dimensão
    dim_day = create_dim(df_cards, "day", "id_day")
    dim_month = create_dim(df_cards, "month", "id_month")
    dim_year = create_dim(df_cards, "year", "id_year")
    dim_hour = create_dim(df_cards, "hour", "id_hour")
    dim_minute = create_dim(df_cards, "minute", "id_minute")

    # criar dim time juntando tudo
    dim_time = (
        df_cards[["day", "month", "year", "hour", "minute"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    # joins para add ids
    dim_time = (
        df_cards[["day", "month", "year", "hour", "minute"]]
        .drop_duplicates()
        .merge(dim_day, on="day")
        .merge(dim_month, on="month")
        .merge(dim_year, on="year")
        .merge(dim_hour, on="hour")
        .merge(dim_minute, on="minute")
        .reset_index(drop=True)
    )
    dim_time.insert(0, "id_time", dim_time.index + 1)
    dim_time = dim_time[
        ["id_time", "id_day", "id_month", "id_year", "id_hour", "id_minute"]
    ]

    # mudando status de nome para id
    status_map = dict(zip(df_status["name_status"], df_status["id_status"]))
    df_cards["id_status"] = df_cards["id_status"].map(status_map)
    df_cards.drop(columns=["created_date"], inplace=True)

    # mudando roles de users para id
    role_map = dict(zip(df_roles["name_role"], df_roles["id_role"]))
    df_users["id_role"] = df_users["name_role"].map(role_map)
    df_users.drop(columns=["name_role"], inplace=True)

    return (
        dim_time,
        dim_day,
        dim_month,
        dim_year,
        dim_hour,
        dim_minute,
        df_cards,
        df_users,
    )


def pipeline_main():
    """
    Main function to run the ETL pipeline.
    """
    # chamando as funções
    df_projects, ids_projects = pipeline_projects()
    df_cards, df_users, df_tags, df_status, df_roles = pipeline_cards(ids_projects)
    dim_time, dim_day, dim_month, dim_year, dim_hour, dim_minute, df_cards, df_users = (
        pipeline_transform(df_cards, df_status, df_users, df_roles)
    )

    # merges de datas
    df_cards = df_cards.merge(dim_day, on="day", how="left")
    df_cards = df_cards.merge(dim_month, on="month", how="left")
    df_cards = df_cards.merge(dim_year, on="year", how="left")
    df_cards = df_cards.merge(dim_hour, on="hour", how="left")
    df_cards = df_cards.merge(dim_minute, on="minute", how="left")

    # merge com dim time para criar os ids referentes as datas
    df_cards = df_cards.merge(
        dim_time,
        on=["id_day", "id_month", "id_year", "id_hour", "id_minute"],
        how="left",
    )

    # função para criar a tabela fato
    def create_fato_cards(df_cards):

        fato_cards = df_cards[
            ["id_card", "id_project", "id_user", "id_status", "id_tag", "id_time"]
        ].copy()
        fato_cards["qtd_cards"] = 1
        fato_cards["id_fato_card"] = fato_cards.index + 1

        fato_cards = fato_cards[
            [
                "id_fato_card",
                "id_card",
                "id_project",
                "id_user",
                "id_status",
                "id_time",
                "id_tag",
                "qtd_cards",
            ]
        ]

        return fato_cards

    fato_cards = create_fato_cards(df_cards)

    return (
        fato_cards,
        df_projects,
        df_cards,
        df_status,
        df_tags,
        df_users,
        df_roles,
        dim_time,
        dim_year,
        dim_month,
        dim_day,
        dim_hour,
        dim_minute,
    )
