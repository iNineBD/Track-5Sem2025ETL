# db/Connectins.py
# %%
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from sqlalchemy.schema import MetaData
from sqlalchemy.exc import SQLAlchemyError

# Importação dos modelos
from ..models import (
    FatoCard,
    DimUser,
    DimTag,
    DimStatus,
    DimRole,
    DimProject,
)

# %%
load_dotenv()

# Configuração do banco
db_url = "postgresql://admin:admin@209.38.145.133:5432/dw_track"
metadata = MetaData(schema="dw_track")
Base = declarative_base(metadata=metadata)
engine = create_engine(db_url, echo=True)
SessionLocal = sessionmaker(bind=engine)


class DBSessionManager:
    def __init__(self):
        self.session = None

    def conectar_banco(self):
        """Cria a conexão e inicializa o banco"""
        try:
            Base.metadata.create_all(engine)
            self.reiniciar_sessao()
            return self.session
        except SQLAlchemyError as e:
            print(f"Erro ao conectar ou consultar o banco: {e}")
            raise

    def reiniciar_sessao(self):
        """Fecha a sessão atual (se existir) e cria uma nova"""
        if self.session:
            self.session.close()
        self.session = SessionLocal()
