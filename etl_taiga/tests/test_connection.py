from unittest import mock
from etl_taiga.db.Connection import DBSessionManager
from sqlalchemy import create_engine


@mock.patch('sqlalchemy.create_engine')  # Patch no create_engine do SQLAlchemy
def test_conectar_banco_cria_sessao(mock_create_engine):
    # Simulando a engine de banco em memória
    mock_create_engine.return_value = create_engine('sqlite:///:memory:')

    # Criando a instância do DBSessionManager
    db = DBSessionManager()

    # Mockando também o método reiniciar_sessao
    with mock.patch.object(db, 'reiniciar_sessao') as mock_reiniciar_sessao:
        # Chamando o método que realiza a conexão
        sessao = db.conectar_banco()

        # Verificando se a sessão foi criada
        assert sessao is not None

        # Verificando se a create_engine foi chamada
        mock_create_engine.assert_called_once_with('sqlite:///:memory:')

        # Verificando se o método reiniciar_sessao foi chamado
        mock_reiniciar_sessao.assert_called_once()
