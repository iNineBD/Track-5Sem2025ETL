import pytest
from peewee import SqliteDatabase

from etl_taiga.models import BaseModel
from etl_taiga.models.dim_platform import DimPlatform

# Criação de banco em memória
test_db = SqliteDatabase(":memory:")


@pytest.fixture(scope="module")
def setup_database():
    # Configura o banco de dados de teste
    BaseModel._meta.database = test_db
    test_db.bind([DimPlatform])
    test_db.connect()
    test_db.create_tables([DimPlatform])
    yield
    test_db.drop_tables([DimPlatform])
    test_db.close()


def test_create_dim_platform(setup_database):
    # Cria um registro de exemplo
    platform = DimPlatform.create(
        name_platform="GitHub"
    )

    # Recupera o registro
    found = DimPlatform.get(DimPlatform.id_platform == platform.id_platform)

    # Verificações
    assert found.name_platform == "GitHub"
    assert isinstance(found.id_platform, int)
