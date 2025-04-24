import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from etl_taiga.src.services import methods


def test_get_auth_success(mocker):
    mock_auth = mocker.patch("etl_taiga.src.services.methods.auth_taiga", return_value="token123")
    token = methods.get_auth()
    assert token == "token123"
    mock_auth.assert_called_once()


def test_get_auth_failure(mocker):
    # mock_auth = mocker.patch("etl_taiga.src.services.methods.auth_taiga", return_value=None)
    with pytest.raises(ValueError, match="Erro ao autenticar no Taiga"):
        methods.get_auth()


def test_get_session(mocker):
    mock_conn = mocker.patch("etl_taiga.src.services.methods.Connection")
    session = methods.get_session()
    mock_conn.assert_called_once()
    assert session == mock_conn.return_value


def test_reset_database_success(mocker):
    mock_session = MagicMock()
    methods.reset_database(mock_session)

    assert mock_session.query.call_count == 6
    mock_session.commit.assert_called_once()


def test_reset_database_exception(mocker):
    mock_session = MagicMock()
    mock_session.query.side_effect = Exception("DB error")

    methods.reset_database(mock_session)

    mock_session.rollback.assert_called_once()


def test_insert_data_success(mocker):
    mock_session = MagicMock()

    # Criando DataFrames de exemplo
    df_example = pd.DataFrame([{"id": 1, "name": "Test"}])
    df_users = pd.DataFrame([{"id": 1, "full_name": "João", "color": "#000", "fk_id_role": 1}])
    df_tags = pd.DataFrame([{"id": 1, "name": "Bug", "color": "#FF0000", "id_card": 1, "id_project": 1}])
    df_status = pd.DataFrame([{"id": 1, "id_card": 1, "id_project": 1}])
    df_facts = pd.DataFrame([{"fk_id_status": 1, "fk_id_tag": 1, "fk_id_user": 1, "fk_id_project": 1, "qtd_card": 10}])

    methods.insert_data(mock_session, df_example, df_example, df_users, df_tags, df_status, df_facts)

    assert mock_session.bulk_insert_mappings.call_count == 6
    mock_session.commit.assert_called_once()


def test_insert_data_failure(mocker):
    mock_session = MagicMock()
    df_example = pd.DataFrame([{"id": 1, "name": "Test"}])

    # Forçamos erro na primeira inserção
    mock_session.bulk_insert_mappings.side_effect = Exception("Insert error")

    methods.insert_data(mock_session, df_example, df_example, df_example, df_example, df_example, df_example)

    mock_session.rollback.assert_called_once()
