import pytest
from peewee import SqliteDatabase

from etl_taiga.models import BaseModel
from etl_taiga.models.dim_card import DimCard

# Banco de dados SQLite em memória para testes
test_db = SqliteDatabase(':memory:')


@pytest.fixture(scope="module")
def setup_database():
    # Substitui o banco do BaseModel pelo de teste
    BaseModel._meta.database = test_db
    test_db.bind([DimCard])  # Vincula a tabela DimCard ao banco
    test_db.connect()
    test_db.create_tables([DimCard])
    yield
    test_db.drop_tables([DimCard])
    test_db.close()


def test_create_dim_card(setup_database):
    # Cria um registro fictício
    card = DimCard.create(
        name_card="Sprint Planning",
        description="Card para planejamento da sprint"
    )

    # Busca no banco
    found = DimCard.get(DimCard.id_card == card.id_card)

    # Verifica os valores
    assert found.name_card == "Sprint Planning"
    assert found.description == "Card para planejamento da sprint"
    assert isinstance(found.id_card, int)
