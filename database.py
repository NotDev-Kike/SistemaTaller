import os
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'fsm_taller.db')}"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class OrdenDB(Base):
  __tablename__ = "ordenes"

  id = Column(Integer, primary_key=True, index=True, autoincrement=True)
  cliente_nombre = Column(String, index=True)
  cliente_celular = Column(String)
  cliente_identidad = Column(String)
  marca = Column(String)
  modelo = Column(String)
  color = Column(String)
  imei = Column(String)
  credenciales = Column(String)
  observaciones = Column(String)
  estado = Column(String, default="Revision")
  fecha = Column(String)


def init_db():
  Base.metadata.create_all(bind=engine)