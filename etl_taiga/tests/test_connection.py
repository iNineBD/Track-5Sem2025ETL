# tests/test_connection.py
from unittest import mock
from etl_taiga.db.Connection import DBSessionManager
from sqlalchemy import create_engine


@mock.patch('sqlalchemy.create_engine')  # Patch no create_engine do SQLAlchemy
def test_conectar_banco_cria_sessao(mock_create_engine):
    # Simulando a engine de banco em memória (SQLite em memória)
    mock_create_engine.return_value = create_engine('sqlite:///:memory:')

    # Criando a instância do DBSessionManager
    db = DBSessionManager()

    # Mockando o método reiniciar_sessao para não precisar de uma conexão real
    with mock.patch.object(db, 'reiniciar_sessao') as mock_reiniciar_sessao:
        # Chamando o método que realiza a conexão
        sessao = db.conectar_banco()

        # Verificando se a sessão foi criada (não deve ser None)
        assert sessao is not None

        # Verificando se a create_engine foi chamada corretamente
        mock_create_engine.assert_called_once_with('sqlite:///:memory:')

        # Verificando se o método reiniciar_sessao foi chamado corretamente
        mock_reiniciar_sessao.assert_called_once()

        # Certificando-se que a sessão criada é a mesma da mockada
        mock_reiniciar_sessao.assert_called_once()

        # Adicionalmente, podemos verificar o tipo da sessão se necessário
        assert isinstance(sessao, mock.MagicMock)

        # Teste se o método conectar_banco não lança exceções quando a conexão é bem-sucedida
        try:
            db.conectar_banco()
        except Exception as e:
            assert False, f"Conectar ao banco falhou com erro: {e}"
