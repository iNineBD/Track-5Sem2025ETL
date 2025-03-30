# %%
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy.schema import MetaData
from sqlalchemy.exc import SQLAlchemyError
# %%
def conectar_banco():

    load_dotenv()
    db_url = "postgresql://admin:admin@209.38.145.133:5432/dw_track"
    if not db_url:
        raise ValueError("A variável de ambiente 'DATABASE_URL' não está definida!")
    metadata = MetaData(schema="dw_track")

    try:
        engine = create_engine(db_url, echo=True)
        Session = sessionmaker(bind=engine)

        session = Session()

        from models import (
            Base,
            FatoCard,
            DimUser,
            DimTag,
            DimStatus,
            DimRole,
            DimProject,
        )

        Base.metadata.create_all(engine)

        statuses = session.query(DimProject).all()
        print(f"🔍 Registros encontrados em DimProject: {len(statuses)}")
        return session

    except SQLAlchemyError as e:
        print(f"erro ao conectar ou consultar o banco: {e}")
        raise

# %%
session = conectar_banco()