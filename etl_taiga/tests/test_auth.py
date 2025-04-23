import requests
from unittest.mock import patch
from etl_taiga.src.services.auth import auth_taiga

@patch("requests.post")
def test_auth_taiga_success(mock_post):
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {"auth_token": "123abc"}
    token = auth_taiga()
    assert token == "123abc"
