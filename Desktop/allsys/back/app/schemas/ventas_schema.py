from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DetalleVentaCreate(BaseModel):
    stock_id: int
    cantidad: int
    precio_unitario: float # El precio que se cobró realmente

class VentaCreate(BaseModel):
    fecha: Optional[datetime] = None
    canal: str 
    vendedor: str 
    metodo_pago: str 
    
    # ✨ NUEVOS CAMPOS
    estado_venta: str = "completada" 
    estado_pago: str = "pagado"
    
    # Datos opcionales del cliente
    nombre_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    identificador_cliente: Optional[str] = None
    
    # Costos extra
    costo_envio: float = 0.0
    descuento_total: float = 0.0
    
    # Logística
    transaccion_id_externo: Optional[str] = None
    empresa_transporte: Optional[str] = None
    numero_seguimiento: Optional[str] = None
    
    detalles: List[DetalleVentaCreate]





class VentaUpdate(BaseModel):
    estado_venta: Optional[str] = None
    estado_pago: Optional[str] = None
    metodo_pago: Optional[str] = None
    nombre_cliente: Optional[str] = None
    email_cliente: Optional[str] = None
    estado_envio: Optional[str] = None
    empresa_transporte: Optional[str] = None
    numero_seguimiento: Optional[str] = None
    notas_internas: Optional[str] = None
    
    # ✨ ESTOS CAMPOS DEBEN ESTAR AQUÍ PARA QUE FASTAPI LOS DEJE PASAR
    total: Optional[float] = None
    subtotal: Optional[float] = None
    costo_envio: Optional[float] = None
    descuento_total: Optional[float] = None