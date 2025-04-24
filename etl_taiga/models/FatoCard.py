from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    ForeignKey,
    TIMESTAMP,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import relationship
# from etl_taiga.db.Connection import Base
from etl_taiga.db.base import Base


class DimUser(Base):
    """tabela dim_user"""
    __tablename__ = "dim_user"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(200), nullable=False)
    color = Column(String(200), nullable=False)
    fk_id_role = Column(Integer, ForeignKey("dim_role.id", ondelete="SET NULL"))
    extend_existing = True

    # relacionamento com dim_role
    role = relationship("DimRole", back_populates="users")

    # relacionamento com fato_card
    fato_cards = relationship("FatoCard", back_populates="dim_user")


class DimTag(Base):
    """tabela dim_tag"""
    __tablename__ = "dim_tag"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    color = Column(String(100), nullable=False)
    id_card = Column(Integer, nullable=True)
    id_project = Column(Integer, nullable=True)
    extend_existing = True

    # relacionamento com fato_card
    fato_cards = relationship("FatoCard", back_populates="dim_tag")


class DimStatus(Base):
    """tabela dim_status"""
    __tablename__ = "dim_status"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    id_card = Column(Integer, nullable=True)
    id_project = Column(Integer, nullable=True)
    extend_existing = True

    # Relacionamento com fato_card
    fato_cards = relationship("FatoCard", back_populates="dim_status")


class DimRole(Base):
    """tabela dim_role"""
    __tablename__ = "dim_role"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    extend_existing = True

    # relacionamento com dim_user
    users = relationship("DimUser", back_populates="role")


class DimProject(Base):
    """tabela dim_project"""
    __tablename__ = "dim_project"

    id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(String(999), nullable=False)
    name = Column(String(200), nullable=False)
    created_date = Column(TIMESTAMP, nullable=False)
    modified_date = Column(TIMESTAMP, nullable=False)
    extend_existing = True

    # relacionamento com fato_card
    fato_cards = relationship("FatoCard", back_populates="dim_project")


class FatoCard(Base):
    """tabela fato_card"""
    __tablename__ = "fato_card"
    __table_args__ = (
        PrimaryKeyConstraint(
            "fk_id_status", "fk_id_tag", "fk_id_user", "fk_id_project"
        ),
    )

    qtd_card = Column(Integer, nullable=False)
    fk_id_status = Column(Integer, ForeignKey("dim_status.id", ondelete="CASCADE"))
    fk_id_tag = Column(Integer, ForeignKey("dim_tag.id", ondelete="CASCADE"))
    fk_id_user = Column(Integer, ForeignKey("dim_user.id", ondelete="CASCADE"))
    fk_id_project = Column(Integer, ForeignKey("dim_project.id", ondelete="CASCADE"))
    extend_existing = True

    # relacionamento com as tabelas dimensionais
    dim_status = relationship("DimStatus", back_populates="fato_cards")
    dim_tag = relationship("DimTag", back_populates="fato_cards")
    dim_user = relationship("DimUser", back_populates="fato_cards")
    dim_project = relationship("DimProject", back_populates="fato_cards")
