import json
from typing import List, Optional
from fastapi import File, UploadFile
from sqlalchemy.orm import Session, joinedload

from app.models.producto_model import Producto
from app.models.variantes_model import Variante
from app.models.talla_model import Talla
from app.models.variante_imagen_model import Imagen
from app.services.s3_service import upload_image_to_s3, delete_image_from_s3


# ===============================
# Crear producto con variantes
# ===============================
from typing import Optional, List
from fastapi import UploadFile
from sqlalchemy.orm import Session
from datetime import datetime
import json

def crear_producto(
    db: Session,
    nombre: str,
    descripcion: str,
    precio: float,
    categoria_id: int,
    marca_id: int,
    variantes: str,
    tipo: str,

    # 🆕 datos de compra
    lugar_compra: Optional[str] = None,
    fecha_compra: Optional[str] = None,  # yyyy-mm-dd
    precio_compra: Optional[float] = None,

    imagenes: Optional[List[UploadFile]] = None
):
    # ---------------- VALIDAR VARIANTES ----------------
    try:
        variantes_data = json.loads(variantes)
    except json.JSONDecodeError:
        raise ValueError("Variantes inválidas")

    # ---------------- CONVERTIR FECHA ----------------
    fecha_compra_date = None
    if fecha_compra:
        fecha_compra_date = datetime.strptime(
            fecha_compra, "%Y-%m-%d"
        ).date()

    # ---------------- CREAR PRODUCTO ----------------
    producto = Producto(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        tipo=tipo,
        categoria_id=categoria_id,
        marca_id=marca_id,
        stock=0,

        # 🆕 guardar datos de compra
        lugar_compra=lugar_compra,
        fecha_compra=fecha_compra_date,
        precio_compra=precio_compra
    )

    db.add(producto)
    db.commit()
    db.refresh(producto)

    # ---------------- VARIANTES ----------------
    _guardar_variantes(db, producto.id, variantes_data, imagenes)

    db.commit()
    return producto


# ===============================
# Función interna para guardar variantes
# ===============================
def _guardar_variantes(
    db: Session,
    producto_id: int,
    variantes_data: list,
    imagenes: Optional[List[UploadFile]] = None
):
    imagen_index = 0

    for v in variantes_data:
        variante = Variante(
            color=v["color"],
            color_nombre=v["colorNombre"],
            precio=v.get("precio", 0),
            descuento=v.get("descuento", 0),
            producto_id=producto_id
        )
        db.add(variante)
        db.flush()

        # Tallas
        for t in v.get("tallas", []):
            talla = Talla(
                talla=t["talla"],
                stock=t["stock"],
                variante_id=variante.id
            )
            db.add(talla)

        # Imágenes
        cantidad_imagenes = len(v.get("imagenesFiles", []))
        if imagenes and cantidad_imagenes > 0:
            for _ in range(cantidad_imagenes):
                file = imagenes[imagen_index]
                url = upload_image_to_s3(file, folder=f"productos/{producto_id}/{variante.id}")
                imagen = Imagen(url=url, variante_id=variante.id)
                db.add(imagen)
                imagen_index += 1


# ===============================
# Obtener producto completo
# ===============================
def obtener_producto_completo(db: Session, producto_id: int):
    return (
        db.query(Producto)
        .options(
            joinedload(Producto.variantes).joinedload(Variante.tallas),
            joinedload(Producto.variantes).joinedload(Variante.imagenes),
            joinedload(Producto.categoria),  # <-- cargar categoría completa
            joinedload(Producto.marca)       # <-- cargar marca
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
# Editar producto (datos generales)
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
    variantes=None,
    imagenes: Optional[List[UploadFile]] = File(None)
):
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        return None

    # ===== PRODUCTO =====
    if nombre is not None:
        producto.nombre = nombre
    if descripcion is not None:
        producto.descripcion = descripcion
    if precio is not None:
        producto.precio = precio
    if categoria_id is not None:
        producto.categoria_id = categoria_id
    if marca_id is not None:
        producto.marca_id = marca_id
    if tipo is not None:
        producto.tipo = tipo

    db.commit()
    db.refresh(producto)

    # ===== VARIANTES =====
    if not variantes:
        variantes_data = []
    elif isinstance(variantes, str):
        variantes_data = json.loads(variantes)
    elif isinstance(variantes, list):
        variantes_data = variantes
    else:
        raise ValueError("Formato inválido de variantes")

    variantes_map = {}
    ids_recibidos = set()  # <-- IDs de variantes enviadas

    for idx, v in enumerate(variantes_data):
        if v.get("id"):
            # ===== VARIANTE EXISTENTE =====
            variante = editar_variante(
                db=db,
                variante_id=v["id"],
                color=v.get("color"),
                color_nombre=v.get("color_nombre"),
                precio=v.get("precio"),
                descuento=v.get("descuento"),
                tallas=v.get("tallas")
            )

            # Eliminar imágenes marcadas
            imagenes_eliminadas = v.get("imagenes_eliminadas", [])
            if imagenes_eliminadas:
                eliminar_imagenes_por_ids(db, imagenes_eliminadas)

            variantes_map[str(variante.id)] = variante
            ids_recibidos.add(variante.id)

        else:
            # ===== NUEVA VARIANTE =====
            nueva_variante = Variante(
                color=v["color"],
                color_nombre=v["color_nombre"],
                precio=v.get("precio", 0),
                descuento=v.get("descuento", 0),
                producto_id=producto.id
            )
            db.add(nueva_variante)
            db.flush()
            db.refresh(nueva_variante)

            # Crear tallas
            for t in v.get("tallas", []):
                talla = Talla(
                    talla=t["talla"],
                    stock=t["stock"],
                    variante_id=nueva_variante.id
                )
                db.add(talla)

            # Subir imágenes de la nueva variante enviadas desde FormData
            if imagenes:
                for file in imagenes:
                    if file.filename.startswith(f"imagenes_nueva_variante_{idx}"):
                        url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{nueva_variante.id}")
                        db.add(Imagen(url=url, variante_id=nueva_variante.id))

            variantes_map[str(nueva_variante.id)] = nueva_variante
            ids_recibidos.add(nueva_variante.id)

    # ===== ELIMINAR VARIANTES REMOVIDAS =====
    variantes_existentes = db.query(Variante).filter(Variante.producto_id == producto.id).all()
    for variante in variantes_existentes:
        if variante.id not in ids_recibidos:
            # eliminar imágenes de S3
            for img in variante.imagenes:
                delete_image_from_s3(img.url)
            db.delete(variante)

    # ===== IMÁGENES ADICIONALES PARA VARIANTES EXISTENTES =====
    if imagenes:
        for file in imagenes:
            try:
                # filename: variante-{id}-{nombreArchivo}
                _, variante_id, _ = file.filename.split("-", 2)
                variante_id = int(variante_id)
            except ValueError:
                continue

            variante = variantes_map.get(str(variante_id))
            if not variante:
                continue

            url = upload_image_to_s3(file, folder=f"productos/{producto.id}/{variante.id}")
            db.add(Imagen(url=url, variante_id=variante.id))

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

    # actualizar campos de variante
    if color is not None:
        variante.color = color
    if color_nombre is not None:
        variante.color_nombre = color_nombre
    if precio is not None:
        variante.precio = precio
    if descuento is not None:
        variante.descuento = descuento

    # manejar tallas
    if tallas is not None:
        # IDs de tallas enviadas desde frontend
        ids_enviados = [t["id"] for t in tallas if "id" in t and t["id"]]

        # 1️⃣ eliminar tallas que ya no existen
        for talla_existente in variante.tallas:
            if talla_existente.id not in ids_enviados:
                db.delete(talla_existente)

        # 2️⃣ actualizar o crear tallas
        for t in tallas:
            if "id" in t and t["id"]:
                # actualizar talla existente
                talla = db.query(Talla).filter(Talla.id == t["id"], Talla.variante_id == variante.id).first()
                if talla:
                    talla.talla = t.get("talla", talla.talla)
                    talla.stock = t.get("stock", talla.stock)
            else:
                # crear nueva talla
                nueva_talla = Talla(
                    talla=t.get("talla", ""),
                    stock=t.get("stock", 0),
                    variante_id=variante.id
                )
                db.add(nueva_talla)

    db.commit()
    db.refresh(variante)
    return variante




# ===============================
# Agregar imágenes a variante
# ===============================
def agregar_imagenes_variante(
    db: Session,
    variante_id: int,
    imagenes: List[UploadFile]
):
    variante = db.query(Variante).filter(Variante.id == variante_id).first()
    if not variante:
        return None

    for file in imagenes:
        url = upload_image_to_s3(file, folder=f"productos/{variante.producto_id}/{variante.id}")
        imagen = Imagen(url=url, variante_id=variante.id)
        db.add(imagen)

    db.commit()
    db.refresh(variante)
    return variante


# ===============================
# Eliminar imagen de variante (DB + S3)
# ===============================
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

    imagenes = (
        db.query(Imagen)
        .filter(Imagen.id.in_(imagen_ids))
        .all()
    )

    for img in imagenes:
        delete_image_from_s3(img.url)
        db.delete(img)





# ===============================
# Eliminar producto completo (con variantes, tallas e imágenes)
# ===============================
def eliminar_producto(db: Session, producto_id: int):
    producto = (
        db.query(Producto)
        .options(
            joinedload(Producto.variantes)
            .joinedload(Variante.imagenes),
            joinedload(Producto.variantes)
            .joinedload(Variante.tallas)
        )
        .filter(Producto.id == producto_id)
        .first()
    )

    if not producto:
        return False

    # ===== ELIMINAR IMÁGENES DE S3 =====
    for variante in producto.variantes:
        for imagen in variante.imagenes:
            try:
                delete_image_from_s3(imagen.url)
            except Exception as e:
                print(f"Error eliminando imagen S3: {imagen.url} -> {e}")

    # ===== ELIMINAR PRODUCTO (cascade borra variantes, tallas e imágenes en BD) =====
    db.delete(producto)
    db.commit()

    return True





