from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PagoCreate(BaseModel):
    monto: float
    metodo_pago: str
    referencia: Optional[str] = None
    notas: Optional[str] = None

class PagoRead(PagoCreate):
    id: int
    fecha: datetime
    class Config:
        from_attributes = True

class EstadisticasConsignacion(BaseModel):
    total_prendas_entregadas: int
    prendas_vendidas: int
    prendas_en_stock: int
    dinero_generado_ventas: float  # Total ventas (PVP)
    dinero_para_cliente: float     # Lo que le debes al cliente
    beneficio_plataforma: float    # Tu ganancia bruta
    dinero_ya_pagado: float        # Pagos realizados
    saldo_pendiente: float         # Lo que falta por pagar