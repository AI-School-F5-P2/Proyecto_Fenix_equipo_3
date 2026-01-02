import json
from typing import List, Optional
from fastapi import File, Form, UploadFile
from sqlalchemy.orm import Session
from app.api.v1 import productos
from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.talla_model import Talla
from app.schemas.producto_schema import ProductoCreate
from sqlalchemy.orm import Session, joinedload
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
    tipo: str,
    imagenes: Optional[List[UploadFile]] = None
):
    try:
        variantes_data = json.loads(variantes)
    except json.JSONDecodeError:
        raise ValueError("Variantes inválidas")

    # 1️⃣ Crear producto
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        tipo=tipo,
        categoria_id=categoria_id,
        marca_id=marca_id,
        stock=0
    )
    db.add(producto)
    db.commit()
    db.refresh(producto)

    # 2️⃣ Crear variantes + tallas
    for v in variantes_data:
        variante = Variante(
            color=v["color"],
            color_nombre=v["colorNombre"],  # ⚠️ solo si existe en el modelo
            precio=v["precio"],
            descuento=v.get("descuento", 0),
            producto_id=producto.id
        )
        db.add(variante)
        db.flush()  # 👈 NO commit aquí

        for t in v["tallas"]:
            talla = Talla(
                talla=t["talla"],
                stock=t["stock"],
                variante_id=variante.id
            )
            db.add(talla)

    db.commit()  # ✅ UN solo commit final

    # 3️⃣ Imágenes (opcional)
    if imagenes:
        for file in imagenes:
            print("Archivo recibido:", file.filename)

    return producto





def obtener_producto_completo(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .options(
            joinedload(Producto.variantes)
            .joinedload(Variante.tallas)
        )
        .filter(Producto.id == producto_id)
        .first()
    )

    if not producto:
        return None

    return producto





def obtener_productos_paginados(
    db: Session,
    page: int = 1,
    limit: int = 10
) -> List[Producto]:
    offset = (page - 1) * limit

    productos = (
        db.query(Producto)
        .options(
            joinedload(Producto.variantes)
            .joinedload(Variante.tallas)
        )
        .order_by(Producto.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return productos