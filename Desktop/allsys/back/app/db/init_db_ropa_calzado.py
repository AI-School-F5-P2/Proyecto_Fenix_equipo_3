from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base

# Importar modelos
# from app.models.categorias_model import Categoria
# from app.models.producto_model import Producto


from app.models.categorias_model import Categoria
from app.models.producto_model import Producto
from app.models.marcas_model import Marca
from app.models.variantes_model import Variante
from app.models.variante_imagen_model import Imagen
from app.models.ventas_model import Venta
from app.models.atributo_model import Atributo, ValorAtributo
from app.models.stock_model import Stock
from app.models.proveedores_model import Proveedor



# ==============================================================================
# 1. DATOS MAESTROS (Estructura Plana y Unificada)
# ==============================================================================

categorias_master = [
    {
        # ==============================================================================
        # 1. ROPA
        # ==============================================================================
        "nombre": "Ropa",
        "descripcion": "Ropa general",
        "genero": "", 
        "hijos": [
            {
                "nombre": "Faldas", 
                "descripcion": "Minifaldas, midi, largas",
                "genero": "mujer",
                "hijos": [
                    {"nombre": "Minifaldas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Faldas por la rodilla", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Faldas midi", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Faldas largas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Faldas asimétricas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Falda-pantalón", "descripcion": "", "genero": "mujer"},
                ]
            },
            {
                "nombre": "Vestidos",
                "genero": "mujer",
                "hijos": [
                    
                    {"nombre": "Vestidos cortos / Mini", "genero": "mujer"},
                    {"nombre": "Vestidos midi", "genero": "mujer"},
                    {"nombre": "Vestidos largos / Maxi", "genero": "mujer"},
                    {"nombre": "Vestidos casuales", "genero": "mujer"},
                    {"nombre": "Vestidos de punto", "genero": "mujer"},
                    {"nombre": "Vestidos camiseros", "genero": "mujer"},
                    {"nombre": "Vestidos de verano / Playeros", "genero": "mujer"},
                    {"nombre": "Vestidos de invierno", "genero": "mujer"},
                    {"nombre": "Ajustados / Bodycon", "genero": "mujer"},
                    {
                        "nombre": "Ocasiones especiales",
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Vestidos de fiesta y cóctel", "genero": "mujer"},
                            {"nombre": "Vestidos de novia", "genero": "mujer"},
                            {"nombre": "Vestidos de graduación", "genero": "mujer"},
                            {"nombre": "Vestidos de noche", "genero": "mujer"},
                        ]
                    }
                ]
            },
            {
                "nombre": "Camisetas y tops",
                "descripcion": "Camisas, blusas, tops",
                "genero": "",
                "hijos": [
                    {"nombre": "Camisetas básicas", "descripcion": "Manga corta lisas", "genero": ""},
                    {"nombre": "Camisetas estampadas", "descripcion": "Gráficas y logos", "genero": ""},
                    {"nombre": "Blusas", "descripcion": "Blusas elegantes", "genero": "mujer"},
                    {"nombre": "Camisas de vestir", "descripcion": "Camisas formales", "genero": "hombre"},
                    {"nombre": "Polos", "descripcion": "", "genero": ""},
                    {"nombre": "Crop tops", "descripcion": "Camisetas cortas", "genero": "mujer"},
                    {"nombre": "Bodies", "descripcion": "Pieza entera", "genero": "mujer"},
                    {"nombre": "Túnicas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Sin mangas", "descripcion": "Tirantes o tank tops", "genero": ""},
                ]
            },
            {
                "nombre": "Pantalones",
                "descripcion": "Partes de abajo",
                "genero": "", 
                "hijos": [
                    {
                        "nombre": "Vaqueros", 
                        "descripcion": "Jeans denim", 
                        "genero": "",
                        "hijos": [
                            {"nombre": "Pitillos / Skinny", "descripcion": "Ajustados", "genero": ""},
                            {"nombre": "Anchos / Wide Leg", "descripcion": "Corte holgado", "genero": ""},
                            {"nombre": "Rectos", "descripcion": "Corte recto clásico", "genero": ""},
                            {"nombre": "Rotos / Desgastados", "descripcion": "Efecto distressed", "genero": ""},
                            {"nombre": "Mom Fit", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Boyfriend", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {"nombre": "Chinos", "descripcion": "Pantalón de tela", "genero": ""},
                    {"nombre": "Leggings", "descripcion": "Mallas ajustadas", "genero": "mujer"},
                    {
                        "nombre": "Pantalones de vestir", 
                        "descripcion": "Sastrería y pinzas", 
                        "genero": "",
                        "hijos": [
                            {"nombre": "Corte Slim", "genero": ""},
                            {"nombre": "Corte Regular", "genero": ""},
                            {"nombre": "Pantalón de pinzas", "genero": ""},
                        ]
                    },
                    {"nombre": "Pantalones cargo", "descripcion": "Bolsillos laterales", "genero": ""},
                    {"nombre": "Joggers", "descripcion": "Pantalones deportivos", "genero": ""},
                    {"nombre": "Shorts y bermudas", "descripcion": "", "genero": ""},
                ]
            },
            {
                # ABRIGOS
                "nombre": "Abrigos y Chaquetas",
                "descripcion": "Prendas de exterior y abrigo",
                "genero": "", 
                "hijos": [
                    {
                        "nombre": "Abrigos",
                        "genero": "",
                        "hijos": [
                            {"nombre": "Abrigos de paño", "genero": ""},
                            {"nombre": "Plumíferos y acolchados", "genero": ""},
                            {"nombre": "Parkas", "genero": ""},
                            {"nombre": "Gabardinas / Trench", "genero": ""},
                            {"nombre": "Impermeables", "genero": ""},
                            {"nombre": "Ponchos y capas", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Cazadoras y Chaquetas",
                        "genero": "",
                        "hijos": [
                            {"nombre": "Cazadoras vaqueras", "genero": ""},
                            {"nombre": "Biker / Cuero", "genero": ""},
                            {"nombre": "Bomber", "genero": ""},
                            {"nombre": "Chaquetas militares", "genero": ""},
                            {"nombre": "Sobrecamisas", "genero": ""},
                            {"nombre": "Cortavientos", "genero": ""},
                        ]
                    },
                    {
                        "nombre": "Americanas y Blazers",
                        "genero": "",
                        "hijos": [
                            {"nombre": "Blazers", "genero": "mujer"},
                            {"nombre": "Americanas clásicas", "genero": "hombre"},
                            {"nombre": "Chalecos de vestir", "genero": ""},
                        ]
                    }
                ]
            },
            {
                # SUDADERAS
                "nombre": "Punto y Sudaderas",
                "descripcion": "",
                "genero": "",
                "hijos": [
                    {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": ""},
                    {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": ""},
                    {
                        "nombre": "Jerséis", 
                        "descripcion": "Jerséis de punto", 
                        "genero": "",
                        "hijos": [
                            {"nombre": "Todos", "descripcion": "", "genero": ""},
                            {"nombre": "Cuello alto", "descripcion": "Turtleneck", "genero": ""},
                            {"nombre": "Cuello de pico", "descripcion": "Escote en V", "genero": ""},
                            {"nombre": "Cuello redondo", "descripcion": "Crew neck", "genero": ""},
                            {"nombre": "Jerséis largos", "descripcion": "Tipo túnica o oversize", "genero": "mujer"},
                            {"nombre": "Jerséis de punto fino", "descripcion": "", "genero": ""},
                            {"nombre": "Jerséis de punto grueso", "descripcion": "", "genero": ""},
                            {"nombre": "Manga 3/4", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {"nombre": "Cárdigans", "descripcion": "", "genero": ""},
                    {"nombre": "Chalecos de punto", "descripcion": "", "genero": ""},
                ]
            },
            {
                # TRAJES
                "nombre": "Trajes y Sastrería",
                "descripcion": "Ropa formal",
                "genero": "hombre",
                "hijos": [
                    {"nombre": "Trajes completos", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Esmoquin", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Chalecos de traje", "descripcion": "", "genero": "hombre"},
                ]
            },
            {
                # ROPA INTERIOR
                "nombre": "Ropa Interior y Pijamas",
                "descripcion": "",
                "genero": "", 
                "hijos": [
                    {"nombre": "Sujetadores", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Braguitas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Tangas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Boxers", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Slips", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Calcetines", "descripcion": "", "genero": ""},
                    {"nombre": "Pijamas", "descripcion": "", "genero": ""},
                    {"nombre": "Albornoces", "descripcion": "", "genero": ""},
                ]
            },
            {
                # ROPA DE BAÑO
                "nombre": "Ropa de baño",
                "descripcion": "Playa y piscina",
                "genero": "",
                "hijos": [
                    {"nombre": "Bikinis", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Bañadores", "descripcion": "Una pieza o short", "genero": ""},
                    {"nombre": "Trikinis", "descripcion": "", "genero": "mujer"},
                ]
            },
        ]
    },
    {
        # ==============================================================================
        # 2. CALZADO
        # ==============================================================================
        "nombre": "Calzado",
        "descripcion": "Zapatos y zapatillas",
        "genero": "",
        "hijos": [
            {
                "nombre": "Zapatillas", 
                "descripcion": "Sneakers y deportivas", 
                "genero": "",
                "hijos": [
                    {"nombre": "Running", "descripcion": "", "genero": ""},
                    {"nombre": "Casual / Lona", "descripcion": "", "genero": ""},
                    {"nombre": "Futbol", "descripcion": "", "genero": ""},
                ]
            },
            {
                "nombre": "Botas y Botines", 
                "descripcion": "", 
                "genero": "",
                "hijos": [
                    {"nombre": "Botas altas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Botines", "descripcion": "", "genero": ""},
                    {"nombre": "Botas de agua", "descripcion": "", "genero": ""},
                    {"nombre": "Botas militares", "descripcion": "", "genero": ""},
                ]
            },
            {
                "nombre": "Zapatos formales", 
                "descripcion": "", 
                "genero": "",
                "hijos": [
                    {"nombre": "Tacones", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Mocasines", "descripcion": "", "genero": ""},
                    {"nombre": "Oxford / Derby", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Alpargatas", "descripcion": "", "genero": ""},
                ]
            },
            {
                "nombre": "Sandalias", 
                "descripcion": "", 
                "genero": "",
                 "hijos": [
                    {"nombre": "Sandalias planas", "descripcion": "", "genero": ""},
                    {"nombre": "Sandalias de tacón", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Chanclas", "descripcion": "", "genero": ""},
                 ]
            }
        ]
    },
    {
        # ==============================================================================
        # 3. BOLSOS
        # ==============================================================================
        "nombre": "Bolsos",
        "descripcion": "",
        "genero": "",
        "hijos":[
            {"nombre": "Mochilas", "descripcion": "", "genero": ""},
            {"nombre": "Bolsas de playa", "descripcion": "", "genero": "mujer"},
            {"nombre": "Maletines", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos cubo", "descripcion": "", "genero": "mujer"},
            {"nombre": "Riñoneras", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos de fiesta", "descripcion": "", "genero": "mujer"},
            {"nombre": "Portatrajes", "descripcion": "", "genero": ""},
            {"nombre": "Bolsa de deporte, Bolso de deporte, bolsa de gimnasio", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos de mano", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos boho", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsas de viaje", "descripcion": "", "genero": ""},
            {"nombre": "Maletas", "descripcion": "", "genero": ""},
            {"nombre": "Neceseres", "descripcion": "", "genero": ""},
            {"nombre": "Satchels", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos de hombro", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos tote", "descripcion": "", "genero": "mujer"},
            {"nombre": "Monederos y carteras", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos de pulseras", "descripcion": "", "genero": "mujer"}
        ]
    },
    {
        # ==============================================================================
        # 4. Accesorios
        # ==============================================================================
        "nombre": "Accesorios",
        "descripcion": "",
        "genero": "",
        "hijos": [
            {"nombre": "Bandanas y pañuelos para el pelo", "descripcion": "", "genero": ""},
            {"nombre": "Cinturones", "descripcion": "", "genero": ""},
            {"nombre": "Guantes", "descripcion": "", "genero": ""},
            {"nombre": "Accesorios de cabello", "descripcion": "", "genero": ""},
            {"nombre": "Pañuelos", "descripcion": "", "genero": ""},
            {"nombre": "Sombreros y gorros", 
             "descripcion": "", 
             "genero": "",
             "hijos": [
                {"nombre": "Pasamontañas", "descripcion": "", "genero": ""},
                {"nombre": "Gorros de lana", "descripcion": "", "genero": ""},
                {"nombre": "Gorros", "descripcion": "", "genero": ""},
                {"nombre": "Orejeras", "descripcion": "", "genero": ""},
                {"nombre": "Tocados", "descripcion": "", "genero": ""},
                {"nombre": "Sombreros", "descripcion": "", "genero": ""},
                {"nombre": "Diademas y cintas", "descripcion": "", "genero": ""},
                ]
            },
            {"nombre": "Joyeria", 
             "descripcion": "", 
             "genero": "",
             "hijos": [
                {"nombre": "Tobilleras", "descripcion": "", "genero": ""},
                {"nombre": "Joyas corporales", "descripcion": "", "genero": ""},
                {"nombre": "Pulsares", "descripcion": "", "genero": ""},
                {"nombre": "Broches", "descripcion": "", "genero": ""},
                {"nombre": "Colgantes y dijes", "descripcion": "", "genero": ""},
                {"nombre": "Pendientes", "descripcion": "", "genero": ""},
                {"nombre": "Conjuntos de joyería", "descripcion": "", "genero": ""},
                {"nombre": "Collares", "descripcion": "", "genero": ""},
                {"nombre": "Anillos", "descripcion": "", "genero": ""},
                ]
            },
            {"nombre": "Llaveros", "descripcion": "", "genero": ""},
            {"nombre": "Bufandas y pañuelos", "descripcion": "", "genero": ""},
            {"nombre": "Gafas de sol", "descripcion": "", "genero": ""},
            {"nombre": "Paraguas", "descripcion": "", "genero": ""},
            {"nombre": "Relojes", "descripcion": "", "genero": ""},
        ]
    },
    {
        # ==============================================================================
        # 5. CUIDADO Y BELLEZA
        # ==============================================================================
        "nombre": "Cuidado y belleza",
        "descripcion": "",
        "genero": "",
        "hijos": [
            {"nombre": "Maquillaje", "descripcion": "", "genero": ""},
            {"nombre": "Perfume", "descripcion": "", "genero": ""},
            {"nombre": "Cuidado facial", "descripcion": "", "genero": ""},
            {"nombre": "Accesorios de belleza", 
             "descripcion": "", 
             "genero": "",
             "hijos": [
                {"nombre": "Utensilios de peluqueria", "descripcion": "", "genero": ""},
                {"nombre": "Accesorios de cuidado facial", "descripcion": "", "genero": ""},
                {"nombre": "Accesorios de cuidado corporal", "descripcion": "", "genero": ""},
                {"nombre": "Herramients de cuidado de uñas", "descripcion": "", "genero": ""},
                {"nombre": "Accesorios de maquillaje", "descripcion": "", "genero": ""}
                ]
            },
            {"nombre": "Cuidado de las manos", "descripcion": "", "genero": ""},
            {"nombre": "Manicura", "descripcion": "", "genero": ""},
            {"nombre": "Cuidado corporal", "descripcion": "", "genero": ""},
            {"nombre": "Cuidado del cabello", "descripcion": "", "genero": ""},
            {"nombre": "Otros productos de belleza", "descripcion": "", "genero": ""}
        ]
    }
]

# ==============================================================================
# 2. LÓGICA DE SINCRONIZACIÓN (UPSERT) - EVITA ERROR DE LLAVES FORÁNEAS
# ==============================================================================

def sincronizar_recursivo(db: Session, nodo: dict, parent_id: int = None):
    nombre = nodo["nombre"]
    
    # 1. Omitir si se llama "Todos"
    if nombre.lower() == "todos":
        return

    # 2. Preparar datos de género
    genero_valor = nodo.get("genero")
    if genero_valor == "": 
        genero_valor = None 

    # 3. Buscar si la categoría ya existe bajo el mismo padre
    categoria = db.query(Categoria).filter(
        Categoria.nombre == nombre,
        Categoria.parent_id == parent_id
    ).first()

    if categoria:
        # Actualizar si ya existe (sin cambiar el ID)
        categoria.genero = genero_valor
        categoria.descripcion = nodo.get("descripcion", "")
        db.flush()
        print(f"🔄 Sincronizada: {nombre}")
    else:
        # Crear si es nueva
        categoria = Categoria(
            nombre=nombre,
            descripcion=nodo.get("descripcion", ""),
            genero=genero_valor,
            parent_id=parent_id
        )
        db.add(categoria)
        db.flush()
        print(f"✨ Creada: {nombre}")

    # 4. Procesar hijos
    for hijo in nodo.get("hijos", []):
        sincronizar_recursivo(db, hijo, parent_id=categoria.id)

def poblar_categorias():
    db = SessionLocal()
    try:
        print("🚀 Iniciando sincronización de categorías...")
        # NOTA: Ya no usamos limpiar_tablas() para evitar errores FK y pérdida de IDs
        for cat in categorias_master:
            sincronizar_recursivo(db, cat)
            
        db.commit()
        print("✅ Categorías actualizadas correctamente sin borrar IDs existentes.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la sincronización: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    poblar_categorias()



























    # "hijos": [
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #         {"nombre": "", "descripcion": "", "genero": ""},
    #     ]