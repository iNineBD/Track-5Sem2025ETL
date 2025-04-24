import pytest
from unittest.mock import MagicMock, patch
from unittest import mock
import requests


# ========================
# Mock do DBSessionManager
# ========================
@pytest.fixture
def mock_db_session():
    """Mock do DBSessionManager para testes sem banco"""
    with patch("etl_taiga.src.services.methods.DBSessionManager") as mock_class:
        mock_session = MagicMock()
        mock_class.return_value.__enter__.return_value = mock_session
        yield mock_session


# ========================
# Mock da função de autenticação
# ========================
@pytest.fixture
def fake_auth_token(monkeypatch):
    """Mocka auth_taiga para evitar chamada real à API"""
    from etl_taiga.src import services
    monkeypatch.setattr(services.auth, "auth_taiga", lambda: "fake-token")
    yield


# ========================
# Mock do requests.post (autenticação)
# ========================
@pytest.fixture
def mock_requests_post(monkeypatch):
    """Mocka requests.post para chamadas de autenticação"""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"auth_token": "fake-token"}

    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: response)
    yield response


# ========================
# Mock do requests.get (dados da API Taiga)
# ========================
@pytest.fixture
def mock_requests_get(monkeypatch):
    """Mocka requests.get para chamadas à API Taiga"""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = [
        {"id": 1, "name": "Exemplo 1"},
        {"id": 2, "name": "Exemplo 2"}
    ]

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: response)
    yield response


# Fixture para mockar o requests.post
@pytest.fixture
def mock_post():
    with mock.patch('requests.post') as mock_post:
        yield mock_post


# Fixture para mockar o requests.get
@pytest.fixture
def mock_get():
    with mock.patch('requests.get') as mock_get:
        yield mock_get
