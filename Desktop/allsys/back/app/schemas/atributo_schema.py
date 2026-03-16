from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class AtributoSchema(BaseModel):
    nombre: str = Field(..., min_length=1)
    valor: Optional[str] = None