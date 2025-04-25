# db/Connection.py
# %%
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
from sqlalchemy.schema import MetaData
from sqlalchemy.exc import SQLAlchemyError
from .base import Base
from .engine import engine, SessionLocal

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
load_dotenv()  # Carrega as variáveis do arquivo .env

# Configuração do banco de dados (carregando a URL do .env)
db_url = os.getenv("DATABASE_URL")  # Puxa a URL diretamente do .env
if not db_url:
    raise ValueError("A variável de ambiente DATABASE_URL não está definida no .env")


class DBSessionManager:
    def __init__(self):
        self.session = None

    def conectar_banco(self):
        """Cria a conexão e inicializa o banco"""
        try:
            Base.metadata.create_all(engine)  # Cria as tabelas no banco se não existirem
            self.reiniciar_sessao()  # Reinicia a sessão
            return self.session
        except SQLAlchemyError as e:
            print(f"Erro ao conectar ou consultar o banco: {e}")
            raise

    def reiniciar_sessao(self):
        """Fecha a sessão atual (se existir) e cria uma nova"""
        if self.session:
            self.session.close()  # Fecha a sessão anterior
        self.session = SessionLocal()  # Cria uma nova sessão
