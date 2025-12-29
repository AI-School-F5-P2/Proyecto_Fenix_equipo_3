import json
from typing import List, Optional
from fastapi import File, Form, UploadFile
from sqlalchemy.orm import Session
from app.api.v1 import productos
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.talla_model import Talla
from app.schemas.producto_schema import ProductoCreate

import json
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.talla_model import Talla

def crear_producto(
    db: Session,
    nombre: str,
    descripcion: str,
    precio: float,
    categoria_id: int,
    marca_id: int,
    variantes: str,
    imagenes: Optional[List[UploadFile]] = None
):
    try:
        variantes_data = json.loads(variantes)
    except json.JSONDecodeError:
        raise ValueError("Variantes inválidas")

    # Crear producto
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        categoria_id=categoria_id,
        marca_id=marca_id
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)

    # Crear variantes y tallas
    for v in variantes_data:
        variante = Variante(
            color=v["color"],
            colorNombre=v["colorNombre"],
            precio=v["precio"],
            descuento=v.get("descuento", 0),
            producto_id=producto.id
        )
        db.add(variante)
        db.commit()
        db.refresh(variante)

        for t in v["tallas"]:
            talla = Talla(
                talla=t["talla"],
                stock=t["stock"],
                variante_id=variante.id
            )
            db.add(talla)

    db.commit()

    # Procesar imágenes si existen
    if imagenes:
        for file in imagenes:
            print(f"Archivo recibido: {file.filename}")
            # Aquí podrías guardarlo en filesystem o cloud

    return producto
