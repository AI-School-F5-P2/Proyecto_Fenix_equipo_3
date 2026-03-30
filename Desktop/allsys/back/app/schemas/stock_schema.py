from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

from app.schemas.atributo_schema import AtributoSchema

class StockSchema(BaseModel):
    # Reglas estrictas:
    id_manual: Optional[int] = None
    stock: int = Field(..., ge=0, description="Las unidades no pueden ser negativas")
    precio_compra: float = Field(..., ge=0, description="El precio de compra no puede ser negativo")
    proveedor: str = Field(..., min_length=1, description="El proveedor es obligatorio")
    fecha_compra: date = Field(..., description="La fecha de compra es obligatoria")
    publicar_web: bool = False
    publicar_vinted: bool = False
    publicar_wallapop: bool = False
    descuento: int = 0
    precio_venta: float = Field(default=0.0)
    etiqueta: str = Field(default="Única")
    proveedor_id: Optional[int] = None
    proveedor_nombre_nuevo: Optional[str] = None
    atributos: List[AtributoSchema] = []
    orden: Optional[int] = 0
    ubicacion: str = Field(..., min_length=1, description="La ubicación en el almacén es obligatoria")