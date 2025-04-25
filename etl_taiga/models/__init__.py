# models/__init__.py
from etl_taiga.db.Connection import Base
from .FatoCard import FatoCard, DimUser, DimTag, DimStatus, DimRole, DimProject
