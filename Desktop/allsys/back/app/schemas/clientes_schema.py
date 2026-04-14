from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ClienteBase(BaseModel):
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    usuario_vinted: Optional[str] = None
    usuario_wallapop: Optional[str] = None
    
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    dni_nie: Optional[str] = None
    
    direccion: Optional[str] = None
    ciudad: Optional[str] = None
    codigo_postal: Optional[str] = None
    provincia: Optional[str] = None
    pais: Optional[str] = "España"
    
    notas_internas: Optional[str] = None
    es_vip: Optional[bool] = False

class ClienteCreate(ClienteBase):
    pass

class ClienteUpdate(ClienteBase):
    pass

class ClienteOut(ClienteBase):
    id: int
    fecha_registro: datetime

    class Config:
        from_attributes = True