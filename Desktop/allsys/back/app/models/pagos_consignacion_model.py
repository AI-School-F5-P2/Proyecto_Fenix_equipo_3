from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class PagoConsignacion(Base):
    __tablename__ = "pagos_consignacion"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id", ondelete="CASCADE"))
    monto = Column(Float, nullable=False)
    fecha = Column(DateTime, default=datetime.utcnow)
    metodo_pago = Column(String(50)) # Transferencia, Bizum, Efectivo
    referencia = Column(String(100), nullable=True) 
    notas = Column(Text, nullable=True) 
    
    cliente = relationship("Cliente")