import pytest
from peewee import IntegrityError, SqliteDatabase

from etl_taiga.models import BaseModel
from etl_taiga.models.DimRole import DimRole
from etl_taiga.models.DimUser import DimUser

# Banco em memória para testes
test_db = SqliteDatabase(":memory:")


@pytest.fixture(scope="module")
def setup_database():
    test_db.bind([DimRole, DimUser], bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables([DimRole, DimUser])
    yield
    test_db.drop_tables([DimUser, DimRole])
    test_db.close()


def test_create_user_with_role(setup_database):
    # Cria um role para o usuário
    role = DimRole.create(name_role="Admin")

    user = DimUser.create(
        name_user="João da Silva", email="joao@email.com", password="1234", id_role=role
    )

    fetched = DimUser.get_by_id(user.id_user)
    assert fetched.name_user == "João da Silva"
    assert fetched.email == "joao@email.com"
    assert fetched.id_role.name_role == "Admin"


def test_create_user_without_required_fields(setup_database):
    role = DimRole.create(name_role="User")

    # Falta o campo name_user
    with pytest.raises(IntegrityError):
        DimUser.create(email="incompleto@email.com", password="", id_role=role)


def test_user_role_relationship(setup_database):
    role = DimRole.create(name_role="Gestor")

    DimUser.create(name_user="Ana", email="ana@email.com", password="123", id_role=role)
    DimUser.create(
        name_user="Bruno", email="bruno@email.com", password="456", id_role=role
    )

    users = list(role.users)
    assert len(users) == 2
    assert {u.name_user for u in users} == {"Ana", "Bruno"}
