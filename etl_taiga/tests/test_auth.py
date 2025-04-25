# tests/test_auth.py
from unittest.mock import patch
from etl_taiga.services.auth import auth_taiga


@patch('etl_taiga.src.services.auth.requests.post')
def test_auth_taiga_mockado(mock_post):
    # Simula a resposta da API do Taiga
    mock_response = mock_post.return_value
    mock_response.status_code = 200
    mock_response.json.return_value = {"auth_token": "token-fake-123"}

    # Chama a função normalmente
    token = auth_taiga()

    # Verificações
    assert token == "token-fake-123"
    mock_post.assert_called_once_with(
        "http://209.38.145.133:9000/api/v1/auth",  # Corrigido aqui
        json={"type": "normal", "username": "taiga-admin", "password": "admin"},
        timeout=10
    )
