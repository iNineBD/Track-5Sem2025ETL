from etl_taiga.db.Connection import DBSessionManager

def test_conectar_banco_cria_sessao():
    db = DBSessionManager()
    sessao = db.conectar_banco()
    assert sessao is not None
