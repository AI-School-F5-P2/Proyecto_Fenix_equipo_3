from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import date

from app.schemas.atributo_schema import AtributoSchema

class StockSchema(BaseModel):
    # Identificadores
    id: Optional[int] = None
    temp_id: Optional[str] = None # ✨ Necesario para que coincida con el Front
    id_manual: Optional[int] = None
    
    # Dueño (Consignación)
    propietario_id: Optional[int] = None # ✨ CRUCIAL: Aquí es donde entra Merlina
    
    # Inventario y Costos
    stock: int = Field(..., ge=0, description="Las unidades no pueden ser negativas")
    precio_compra: float = Field(..., ge=0, description="El precio de compra no puede ser negativo")
    
    # Proveedor (Ahora acepta vacíos sin rechistar)
    proveedor: Optional[str] = "" 
    proveedor_id: Optional[int] = None
    proveedor_nombre_nuevo: Optional[str] = None
    
    # Logística
    fecha_compra: date = Field(..., description="La fecha de compra es obligatoria")
    ubicacion: str = Field(default="", description="Ubicación en almacén") # ✨ Quitamos el min_length=1 por seguridad
    etiqueta: str = Field(default="Única")
    orden: Optional[int] = 0
    
    # Venta y Canales
    precio_venta: float = Field(default=0.0)
    descuento: int = 0
    publicar_web: bool = False
    publicar_vinted: bool = False
    publicar_wallapop: bool = False
    
    # Atributos EAV
    atributos: List[AtributoSchema] = []

    class Config:
        # Esto permite que si el front envía "stock", Pydantic lo asigne a "stock"
        # y si envía "cantidad", también funcione si lo mapeas.
        populate_by_name = True

class StockEditPayload(BaseModel):
    cantidad: int
    precio_compra: float
    precio_venta: float
    descuento: float = 0
    ubicacion: Optional[str] = ""
    fecha_compra: Optional[str] = None
    proveedor_id: Optional[int] = None
    proveedor_nombre_nuevo: Optional[str] = None
    publicar_web: bool = False
    publicar_vinted: bool = False
    publicar_wallapop: bool = False
    atributos: Optional[List[Dict[str, Any]]] = []