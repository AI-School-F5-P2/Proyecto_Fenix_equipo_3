from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DetalleVentaCreate(BaseModel):
    stock_id: int
    cantidad: int
    precio_unitario: float # El precio que se cobró realmente

class VentaCreate(BaseModel):
    fecha: Optional[datetime] = None
    canal: str # web, tienda, vinted, wallapop
    vendedor: str # Yenny, Maikol, Paola, sistema_web
    metodo_pago: str # efectivo, tarjeta, stripe, etc.
    
    # Datos opcionales del cliente
    nombre_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    
    # Costos extra
    costo_envio: float = 0.0
    descuento_total: float = 0.0
    
    # Logística (opcional al inicio)
    transaccion_id_externo: Optional[str] = None
    empresa_transporte: Optional[str] = None
    numero_seguimiento: Optional[str] = None
    
    detalles: List[DetalleVentaCreate]





class VentaUpdate(BaseModel):
    # Estados
    estado_venta: Optional[str] = None # procesando, enviada, completada, cancelada, devuelta
    estado_pago: Optional[str] = None # pendiente, pagado, reembolsado
    metodo_pago: Optional[str] = None
    
    # Cliente
    nombre_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    notas_internas: Optional[str] = None
    
    # Logística
    estado_envio: Optional[str] = None
    direccion_envio: Optional[str] = None
    empresa_transporte: Optional[str] = None
    numero_seguimiento: Optional[str] = None