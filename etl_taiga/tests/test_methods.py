import pandas as pd
from unittest.mock import MagicMock
from etl_taiga.src.services.methods import insert_data, reset_database

def test_reset_database_success():
    mock_session = MagicMock()
    reset_database(mock_session)
    assert mock_session.commit.called

def test_insert_data_success():
    mock_session = MagicMock()
    df = pd.DataFrame([{"id": 1, "name": "Exemplo", "description": "...", "created_date": "2024-01-01", "modified_date": "2024-01-02"}])
    insert_data(mock_session, df, df, df, df, df, df)
    assert mock_session.commit.called
