# app/models/talla_model.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Talla(Base):
    __tablename__ = "tallas"

    id = Column(Integer, primary_key=True, index=True)
    variante_id = Column(Integer, ForeignKey("variantes.id", ondelete="CASCADE"))

    talla = Column(String(20), nullable=False)
    stock = Column(Integer, nullable=False)

    variante = relationship("Variante", back_populates="tallas")
