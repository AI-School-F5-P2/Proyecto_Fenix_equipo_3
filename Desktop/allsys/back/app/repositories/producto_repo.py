import json
import random
import string
from typing import List, Optional
from fastapi import UploadFile
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.talla_model import Talla
from app.models.variante_imagen_model import Imagen
from app.services.s3_service import upload_image_to_s3, delete_image_from_s3

# ===============================
# Funciones para generar SKU camuflado
# ===============================
def codificar_id(id_unico: int, length: int = 4) -> str:
    """
    Codifica el ID en un bloque alfanumérico de longitud fija.
    Mezcla el ID con letras aleatorias.
    """
    letras = ''.join(random.choices(string.ascii_uppercase, k=length))
    return f"{letras}{id_unico}"

def generar_sku_camuflado(tipo: str, id_unico: int) -> str:
    """
    Genera SKU camuflado: letra inicial del tipo + bloque aleatorio + ID codificado
    Ej: R-H3KT4-AB27
    """
    inicial = tipo[0].upper() if tipo else "X"
    bloque_aleatorio = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    id_codificado = codificar_id(id_unico)
    return f"{inicial}-{bloque_aleatorio}-{id_codificado}"


# ===============================
# Crear producto con variantes
# ===============================
def crear_producto(
    db: Session,
    nombre: str,
    descripcion: str,
    precio: float,
    categoria_id: int,
    marca_id: int,
    variantes: str,
    tipo: str,
    lugar_compra: Optional[str] = None,
    fecha_compra: Optional[str] = None,
    precio_compra: Optional[float] = None,
    imagenes: Optional[List[UploadFile]] = None
):
    # Validar variantes
    try:
        variantes_data = json.loads(variantes)
    except json.JSONDecodeError:
        raise ValueError("Variantes inválidas")

    # Convertir fecha de compra
    fecha_compra_date = None
    if fecha_compra:
        fecha_compra_date = datetime.strptime(fecha_compra, "%Y-%m-%d").date()

    # Generar un SKU temporal
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        tipo=tipo,
        categoria_id=categoria_id,
        marca_id=marca_id,
        stock=0,
        lugar_compra=lugar_compra,
        fecha_compra=fecha_compra_date,
        precio_compra=precio_compra,
        sku="TEMP"  # cualquier valor temporal
    )
    db.add(producto)
    db.flush()  # ahora asigna ID

    # Generar SKU real usando el ID asignado
    producto.sku = generar_sku_camuflado(tipo=tipo, id_unico=producto.id)
    db.commit()
    db.refresh(producto)

    # Guardar variantes
    _guardar_variantes(db, producto, variantes_data, imagenes)

    return producto


# ===============================
# Función interna para guardar variantes
# ===============================
def _guardar_variantes(
    db: Session,
    producto: Producto,
    variantes_data: list,
    imagenes: Optional[List[UploadFile]] = None
):
    imagen_index = 0
    for v in variantes_data:
        variante = Variante(
            color=v["color"],
            color_nombre=v["color_nombre"],
            precio=v.get("precio", 0),
            descuento=v.get("descuento", 0),
            producto_id=producto.id,
            sku="TEMP"  # temporal
        )
        db.add(variante)
        db.flush()  # ahora tiene ID

        # Generar SKU final
        variante.sku = generar_sku_camuflado(tipo=producto.tipo, id_unico=variante.id)

        # Guardar tallas
        for t in v.get("tallas", []):
            db.add(Talla(
                talla=t["talla"],
                stock=t["stock"],
                variante_id=variante.id
            ))

        # Guardar imágenes
        cantidad_imagenes = len(v.get("imagenesFiles", []))
        if imagenes and cantidad_imagenes > 0:
            for _ in range(cantidad_imagenes):
                file = imagenes[imagen_index]
                url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{variante.id}")
                db.add(Imagen(url=url, variante_id=variante.id))
                imagen_index += 1

    db.commit()


# ===============================
# Obtener producto completo
# ===============================
def obtener_producto_completo(db: Session, producto_id: int):
    return (
        db.query(Producto)
        .options(
            joinedload(Producto.variantes).joinedload(Variante.tallas),
            joinedload(Producto.variantes).joinedload(Variante.imagenes),
            joinedload(Producto.categoria),
            joinedload(Producto.marca)
        )
        .filter(Producto.id == producto_id)
        .first()
    )


# ===============================
# Obtener productos paginados
# ===============================
def obtener_productos_paginados(db: Session, page: int = 1, limit: int = 10) -> List[Producto]:
    offset = (page - 1) * limit
    return (
        db.query(Producto)
        .options(joinedload(Producto.variantes).joinedload(Variante.tallas))
        .order_by(Producto.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# ===============================
# Editar producto completo y variantes
# ===============================
def editar_producto_completo(
    db: Session,
    producto_id: int,
    nombre: Optional[str] = None,
    descripcion: Optional[str] = None,
    precio: Optional[float] = None,
    categoria_id: Optional[int] = None,
    marca_id: Optional[int] = None,
    tipo: Optional[str] = None,
    lugar_compra: Optional[str] = None,
    fecha_compra: Optional[str] = None,
    precio_compra: Optional[float] = None,
    variantes: Optional[str] = None,
    imagenes: Optional[List[UploadFile]] = None
):
    producto = db.query(Producto).options(
        joinedload(Producto.variantes).joinedload(Variante.tallas),
        joinedload(Producto.variantes).joinedload(Variante.imagenes)
    ).filter(Producto.id == producto_id).first()

    if not producto:
        return None

    # Actualizar producto
    if nombre: producto.nombre = nombre
    if descripcion: producto.descripcion = descripcion
    if precio: producto.precio = precio
    if categoria_id: producto.categoria_id = categoria_id
    if marca_id: producto.marca_id = marca_id
    if tipo: 
        producto.tipo = tipo
        # Actualizar SKU del producto si cambia tipo
        producto.sku = generar_sku_camuflado(tipo=tipo, id_unico=producto.id)
    if lugar_compra: producto.lugar_compra = lugar_compra
    if fecha_compra: producto.fecha_compra = datetime.strptime(fecha_compra, "%Y-%m-%d").date()
    if precio_compra: producto.precio_compra = precio_compra

    db.commit()
    db.refresh(producto)

    # Actualizar variantes
    variantes_data = json.loads(variantes) if variantes else []
    ids_recibidos = set()

    for idx, v in enumerate(variantes_data):
        if v.get("id"):
            variante = db.query(Variante).filter(Variante.id == v["id"], Variante.producto_id == producto.id).first()
            if not variante: continue
            variante.color = v.get("color", variante.color)
            variante.color_nombre = v.get("color_nombre", variante.color_nombre)
            variante.precio = v.get("precio", variante.precio)
            variante.descuento = v.get("descuento", variante.descuento)
        else:
            variante = Variante(
                color=v["color"],
                color_nombre=v["color_nombre"],
                precio=v.get("precio", 0),
                descuento=v.get("descuento", 0),
                producto_id=producto.id
            )
            db.add(variante)
            db.flush()
            variante.sku = generar_sku_camuflado(tipo=producto.tipo, id_unico=variante.id)

        # Guardar tallas
        for t in v.get("tallas", []):
            if "id" in t and t["id"]:
                talla = db.query(Talla).filter(Talla.id == t["id"], Talla.variante_id == variante.id).first()
                if talla:
                    talla.talla = t.get("talla", talla.talla)
                    talla.stock = t.get("stock", talla.stock)
            else:
                db.add(Talla(talla=t.get("talla", ""), stock=t.get("stock", 0), variante_id=variante.id))

        # Guardar imágenes
        if imagenes:
            for file in imagenes:
                if file.filename.startswith(f"imagenes_nueva_variante_{idx}"):
                    url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{variante.id}")
                    db.add(Imagen(url=url, variante_id=variante.id))

        ids_recibidos.add(variante.id)

    # Eliminar variantes borradas
    for variante in producto.variantes:
        if variante.id not in ids_recibidos:
            for img in variante.imagenes:
                delete_image_from_s3(img.url)
            db.delete(variante)

    db.commit()
    db.refresh(producto)
    return producto


# ===============================
# Editar variante + tallas
# ===============================
def editar_variante(
    db: Session,
    variante_id: int,
    color: Optional[str] = None,
    color_nombre: Optional[str] = None,
    precio: Optional[float] = None,
    descuento: Optional[float] = None,
    tallas: Optional[List[dict]] = None
):
    variante = db.query(Variante).filter(Variante.id == variante_id).first()
    if not variante:
        return None

    if color is not None: variante.color = color
    if color_nombre is not None: variante.color_nombre = color_nombre
    if precio is not None: variante.precio = precio
    if descuento is not None: variante.descuento = descuento

    if tallas is not None:
        ids_enviados = [t["id"] for t in tallas if "id" in t and t["id"]]
        for talla_existente in variante.tallas:
            if talla_existente.id not in ids_enviados:
                db.delete(talla_existente)

        for t in tallas:
            if "id" in t and t["id"]:
                talla = db.query(Talla).filter(Talla.id == t["id"], Talla.variante_id == variante.id).first()
                if talla:
                    talla.talla = t.get("talla", talla.talla)
                    talla.stock = t.get("stock", talla.stock)
            else:
                db.add(Talla(talla=t.get("talla", ""), stock=t.get("stock", 0), variante_id=variante.id))

    db.commit()
    db.refresh(variante)
    return variante


# ===============================
# Funciones de imágenes
# ===============================
def agregar_imagenes_variante(db: Session, variante_id: int, imagenes: List[UploadFile]):
    variante = db.query(Variante).filter(Variante.id == variante_id).first()
    if not variante:
        return None
    for file in imagenes:
        url = upload_image_to_s3(file, folder=f"productos/{variante.producto_id}/{variante.id}")
        db.add(Imagen(url=url, variante_id=variante.id))
    db.commit()
    db.refresh(variante)
    return variante

def eliminar_imagen_variante(db: Session, imagen_id: int):
    imagen = db.query(Imagen).filter(Imagen.id == imagen_id).first()
    if not imagen:
        return False
    delete_image_from_s3(imagen.url)
    db.delete(imagen)
    db.commit()
    return True

def eliminar_imagenes_por_ids(db: Session, imagen_ids: list[int]):
    if not imagen_ids:
        return
    imagenes = db.query(Imagen).filter(Imagen.id.in_(imagen_ids)).all()
    for img in imagenes:
        delete_image_from_s3(img.url)
        db.delete(img)
    db.commit()


# ===============================
# Eliminar producto completo
# ===============================
def eliminar_producto(db: Session, producto_id: int):
    producto = db.query(Producto).options(
        joinedload(Producto.variantes).joinedload(Variante.imagenes),
        joinedload(Producto.variantes).joinedload(Variante.tallas)
    ).filter(Producto.id == producto_id).first()

    if not producto:
        return False

    for variante in producto.variantes:
        for imagen in variante.imagenes:
            try:
                delete_image_from_s3(imagen.url)
            except Exception as e:
                print(f"Error eliminando imagen S3: {imagen.url} -> {e}")

    db.delete(producto)
    db.commit()
    return True
