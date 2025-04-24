# etl_taiga/tests/test_connection.py

from unittest import mock
from etl_taiga.db.Connection import DBSessionManager

def test_conectar_banco_cria_sessao():
    # Mockando a função create_engine para que não se conecte ao banco de dados real
    with mock.patch('sqlalchemy.create_engine') as mock_create_engine:
        # Configurando o mock para retornar uma conexão simulada
        mock_create_engine.return_value = mock.Mock()

        # Criando o objeto DBSessionManager
        db = DBSessionManager()

        # Mockando também o método reiniciar_sessao, que é chamado dentro de conectar_banco
        with mock.patch.object(db, 'reiniciar_sessao') as mock_reiniciar_sessao:
            # Chamando o método conectar_banco, que deve usar o mock
            sessao = db.conectar_banco()

            # Assegurando que a sessão não seja None
            assert sessao is not None

            # Verificando se a função create_engine foi chamada (garante que o mock foi utilizado)
            mock_create_engine.assert_called_once()

            # Verificando se o método reiniciar_sessao foi chamado
            mock_reiniciar_sessao.assert_called_once()
