# tests/test_get_data.py
import pytest
from unittest.mock import patch
import pandas as pd

from etl_taiga.services import get_data


@pytest.fixture
def mock_fetch_data():
    with patch("etl_taiga.src.services.get_data.fetch_data") as mock:
        yield mock


def test_pipeline_projets(mock_fetch_data):
    mock_fetch_data.return_value = [
        {"id": 1, "name": "Projeto 1", "description": "Desc", "created_date": "2023-01-01", "modified_date": "2023-01-02"}
    ]

    df = get_data.pipeline_projets()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["id", "name", "description", "created_date", "modified_date"]
    assert len(df) == 1


def test_pipeline_roles(mock_fetch_data):
    mock_fetch_data.return_value = [
        {"id": 1, "name": "Dev"},
        {"id": 2, "name": "Dev"}  # duplicated name to test deduplication
    ]

    df = get_data.pipeline_roles()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["id", "name"]
    assert len(df) == 1  # duplicated name should be dropped
    assert df.iloc[0]["name"] == "Dev"


def test_pipeline_users(mock_fetch_data):
    mock_fetch_data.return_value = [
        {"id": 1, "full_name_display": "João", "color": "#123456"},
        {"id": 2, "full_name_display": "Maria", "color": "#abcdef"},
    ]


def test_pipeline_tags(mock_fetch_data):
    mock_fetch_data.return_value = [
        {
            "id": 1,
            "tags": [{"name": "Urgente", "color": "#FF0000"}],
            "project": 101
        },
        {
            "id": 2,
            "tags": None,
            "project": 101
        },
        {
            "id": 3,
            "tags": [{"name": "Melhoria", "color": None}],
            "project": 101
        },
    ]

    df = get_data.pipeline_tags()
    assert isinstance(df, pd.DataFrame)
    assert "name" in df.columns
    assert df["color"].str.startswith("#").all()
    assert df["id_card"].nunique() >= 1


def test_pipeline_status(mock_fetch_data):
    mock_fetch_data.return_value = [
        {
            "id": 1,
            "status_extra_info": {"name": "To Do"},
            "project": 100
        },
        {
            "id": 2,
            "status_extra_info": {"name": "Done"},
            "project": 100
        }
    ]

    df = get_data.pipeline_status()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns).count("name") == 1
    assert df["id_project"].nunique() == 1


def test_pipeline_fact_cards(mock_fetch_data):
    # mock para pipeline_tags e pipeline_status
    def side_effect(endpoint):
        if endpoint == "userstories":
            return [
                {
                    "id": 1,
                    "tags": [{"name": "Urgente", "color": "#FF0000"}],
                    "project": 10,
                    "status_extra_info": {"name": "In Progress"},
                    "assigned_to": 1
                },
                {
                    "id": 2,
                    "tags": [{"name": "Bug", "color": "#000000"}],
                    "project": 10,
                    "status_extra_info": {"name": "Done"},
                    "assigned_to": 1
                }
            ]
        return []

    mock_fetch_data.side_effect = side_effect

    df = get_data.pipeline_fact_cards()
    assert isinstance(df, pd.DataFrame)
    assert df.shape[1] == 5
    assert set(df.columns) == {
        "fk_id_status", "fk_id_tag", "fk_id_user", "fk_id_project", "qtd_card"
    }
