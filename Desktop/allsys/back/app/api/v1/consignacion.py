from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_session
from app.schemas.consignacion_schema import EstadisticasConsignacion, PagoCreate, PagoRead, PrendaClienteDetalle
from app.repositories import consignacion_repo
from typing import List

router = APIRouter(prefix="/consignacion", tags=["Consignación"])

@router.get("/cliente/{cliente_id}/stats", response_model=EstadisticasConsignacion)
def get_stats(cliente_id: int, db: Session = Depends(get_session)):
    return consignacion_repo.obtener_estadisticas_cliente(db, cliente_id)

@router.post("/cliente/{cliente_id}/pagar", response_model=PagoRead)
def pay_client(cliente_id: int, data: PagoCreate, db: Session = Depends(get_session)):
    return consignacion_repo.registrar_pago(db, cliente_id, data)

@router.get("/cliente/{cliente_id}/pagos", response_model=list[PagoRead])
def get_payments(cliente_id: int, db: Session = Depends(get_session)):
    return consignacion_repo.listar_pagos(db, cliente_id)

from typing import Optional
from fastapi import Query

@router.get("/cliente/{cliente_id}/prendas")
def get_client_items_detail(
    cliente_id: int, 
    page: int = Query(1, ge=1), 
    limit: int = Query(20, ge=1), 
    db: Session = Depends(get_session)
):
    return consignacion_repo.listar_prendas_detalle_cliente(db, cliente_id, page, limit)