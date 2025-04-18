# %%
import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from sqlalchemy.schema import MetaData
from sqlalchemy.exc import SQLAlchemyError

# %%
load_dotenv()

# Configuração do banco
db_url = "postgresql://admin:admin@209.38.145.133:5432/dw_track"
metadata = MetaData(schema="dw_track")
Base = declarative_base(metadata=metadata)
engine = create_engine(db_url, echo=True)
Session = sessionmaker(bind=engine)
session = None  # Variável global para a sessão

# Importação dos modelos
from ..models import (
    FatoCard,
    DimUser,
    DimTag,
    DimStatus,
    DimRole,
    DimProject,
)


def conectar_banco():
    """Cria a conexão e inicializa o banco"""
    global session  # Usa a sessão global
    try:
        Base.metadata.create_all(engine)  # Garante que as tabelas existem
        reiniciar_sessao()  # Reinicia a sessão
        return session
    except SQLAlchemyError as e:
        print(f"Erro ao conectar ou consultar o banco: {e}")
        raise


def reiniciar_sessao():
    """Fecha a sessão atual (se existir) e cria uma nova"""
    global session
    if session:
        session.close()  # Fecha a sessão anterior
    session = Session()  # Cria uma nova sessão
