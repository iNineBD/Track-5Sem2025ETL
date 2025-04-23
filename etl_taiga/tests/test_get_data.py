import pandas as pd
from unittest.mock import patch
from etl_taiga.src.services import get_data

@patch("etl_taiga.src.services.get_data.fetch_data")
def test_pipeline_projects(mock_fetch):
    mock_fetch.return_value = [
        {"id": 1, "name": "Projeto A", "description": "...", "created_date": "2024-01-01", "modified_date": "2024-01-02"}
    ]
    df = get_data.pipeline_projets()
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
