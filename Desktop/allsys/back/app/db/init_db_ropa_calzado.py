from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base

# Importar modelos
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
# 1. DATOS MAESTROS (Estructura: Categoría -> Género -> Tipo de Prenda)
# ==============================================================================

categorias_master = [
    {
        # ==============================================================================
        # 1. ROPA
        # ==============================================================================
        "nombre": "Ropa",
        "descripcion": "Ropa en general",
        "genero": "", 
        "hijos": [
            {
                # ----------------------------------------------------------------------
                # ROPA MUJER
                # ----------------------------------------------------------------------
                "nombre": "Mujer",
                "descripcion": "Ropa para mujer",
                "genero": "mujer",
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
                            {"nombre": "Vestidos vaqueros", "genero": "mujer"},
                            {"nombre": "Vestidos de punto", "genero": "mujer"},
                            {"nombre": "Vestidos camiseros", "genero": "mujer"},
                            {"nombre": "Vestidos formales", "genero": "mujer"},
                            {"nombre": "Vestidos informales", "genero": "mujer"},
                            {"nombre": "Vestidos sin tirantes", "genero": "mujer"},
                            {"nombre": "Vestidos negros", "genero": "mujer"},
                            {"nombre": "Vestidos de verano / Playeros", "genero": "mujer"},
                            {"nombre": "Vestidos de invierno", "genero": "mujer"},
                            {
                                "nombre": "Ocasiones especiales",
                                "genero": "mujer",
                                "hijos": [
                                    {"nombre": "Vestidos de fiesta y cóctel", "genero": "mujer"},
                                    {"nombre": "Vestidos de novia", "genero": "mujer"},
                                    {"nombre": "Vestidos de graduación", "genero": "mujer"},
                                    {"nombre": "Vestidos de noche", "genero": "mujer"},
                                    {"nombre": "Espalda descubierta", "genero": "mujer"},
                                ]
                            },
                            {"nombre": "Otros vestidos", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Camisetas y tops",
                        "descripcion": "Camisas, blusas, tops",
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Camisas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "blusas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "chalecos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Camisetas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Sin mangas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Túnicas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Crop tops", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Manga corta", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Manga 3/4", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Manga Larga", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Bodies", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Hombros descubiertos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Cuello alto", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Peplum", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Halter", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Otros tops", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Vaqueros",
                        "descripcion": "Partes de abajo",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Vaqueros boyfriend", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros tobilleros", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros de campana", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros de cintura alta", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros rotos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros pitillo", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros rectos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Otros Vaqueros", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Pantalones y leggins",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Pantalones tobilleros y chinos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones anchos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones ptitillo", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones de pinzas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones rectos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones de cuero", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Leggins", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones harén", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Otros Pantalones", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Shorts",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "De cintura baja", "descripcion": "", "genero": "mujer"},
                            {"nombre": "De cintura alta", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Hasta la rodilla", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vaqueros cortos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "De encaje", "descripcion": "", "genero": "mujer"},
                            {"nombre": "De cuero cortos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Estilo cargo mujer", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Capri", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Otros shorts", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Monos",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Monos largos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Monos cortos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Otros monos", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Abrigos y Chaquetas",
                        "descripcion": "Prendas de exterior",
                        "genero": "mujer", 
                        "hijos": [
                            {
                                "nombre": "Abrigos",
                                "genero": "mujer",
                                "hijos": [
                                    {"nombre": "Trencas", "genero": "mujer"},
                                    {"nombre": "Sobretodos y abrigos largos", "genero": "mujer"},
                                    {"nombre": "Parkas", "genero": "mujer"},
                                    {"nombre": "Chaquetones marineros", "genero": "mujer"},
                                    {"nombre": "Impermeables", "genero": "mujer"},
                                    {"nombre": "Gabardinas", "genero": "mujer"},
                                ]
                            },
                            {"nombre": "Chalecos", "genero": "mujer"},
                            {
                                "nombre": "Chaquetas",
                                "genero": "mujer",
                                "hijos": [
                                    {"nombre": "Cazadoras bikers", "genero": "mujer"},
                                    {"nombre": "Chaquetas bombers", "genero": "mujer"},
                                    {"nombre": "Cazadoras vaqueras", "genero": "mujer"},
                                    {"nombre": "Chaquetas militares y utilitarias", "genero": "mujer"},
                                    {"nombre": "Forros polares", "genero": "mujer"},
                                    {"nombre": "Chaquetas harrington", "genero": "mujer"},
                                    {"nombre": "Chaquetas de plumas", "genero": "mujer"},
                                    {"nombre": "Chaquetas acolchadas", "genero": "mujer"},
                                    {"nombre": "Sobrecamisas", "genero": "mujer"},
                                    {"nombre": "Chaquetas de esquí y snow", "genero": "mujer"},
                                    {"nombre": "Chaquetas universitarias", "genero": "mujer"},
                                    {"nombre": "Cortavientos", "genero": "mujer"},
                                ]
                            },
                            {"nombre": "Ponchos", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Jerséis y sudaderas",
                        "descripcion": "",
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "mujer"},
                            {
                                "nombre": "Jerséis", 
                                "descripcion": "Jerséis de punto", 
                                "genero": "mujer",
                                "hijos": [
                                    {"nombre": "Cuello alto", "descripcion": "Turtleneck", "genero": "mujer"},
                                    {"nombre": "Cuello de pico", "descripcion": "Escote en V", "genero": "mujer"},
                                    {"nombre": "Cuello redondo", "descripcion": "Crew neck", "genero": "mujer"},
                                    {"nombre": "Jerséis largos", "descripcion": "Tipo túnica o oversize", "genero": "mujer"},
                                    {"nombre": "Jerséis de punto fino", "descripcion": "", "genero": "mujer"},
                                    {"nombre": "Jerséis de punto grueso", "descripcion": "", "genero": "mujer"},
                                    {"nombre": "Manga 3/4", "descripcion": "", "genero": "mujer"},
                                ]
                            },
                            {"nombre": "Kimonos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Cárdigan", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Boleros", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Chalecos de punto", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Trajes y blazers Mujer",
                        "descripcion": "",
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Blazers", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Trajes de pantalón", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Trajes de falda", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Ropa de baño Mujer",
                        "descripcion": "Playa y piscina",
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Bikinis", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Bañadores", "descripcion": "Una pieza o short", "genero": "mujer"},
                            {"nombre": "Trikinis", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pareos y caftanes", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Lencería y pijamas Mujer",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Sujetadores", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Braguitas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Conjuntos de lencería", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Lencería moldeadora", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pijamas Mujer", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Batas Mujer", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Medias", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Calcetines Mujer", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Accesorios de lencería", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Premamá",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Camisetas y blusas premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Vestidos premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Faldas premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Pantalones premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Shorts premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Monos premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Sudaderas y jerseís premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Abrigos y cazadoras premamá", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Bañadores y pareos premamá", "descripcion": "", "genero": "mujer"},
                            {
                                "nombre": "Ropa interior premamá", 
                                "descripcion": "", 
                                "genero": "mujer",
                                "hijos":[
                                    {"nombre": "Braguitas premamá", "descripcion": "", "genero": "mujer"},
                                    {"nombre": "Pijamas premamá", "descripcion": "", "genero": "mujer"},
                                    {"nombre": "Sujetadores premamá y posparto", "descripcion": "", "genero": "mujer"},
                                ]
                            },
                            {"nombre": "Ropa de deporte premamá", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {
                        "nombre": "Ropa deportiva Mujer",
                        "descripcion": "",
                        "genero": "mujer", 
                        "hijos": [
                            {"nombre": "Tops y camisetas deportivas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Sujetadores deportivos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Leggins y pantalones deportivos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Chándales Mujer", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Shorts deportivos", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Faldas deportivas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Sudaderas deportivas", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Chaquetas deportivas", "descripcion": "", "genero": "mujer"},
                        ]
                    }
                ]
            },
            {
                # ----------------------------------------------------------------------
                # ROPA HOMBRE
                # ----------------------------------------------------------------------
                "nombre": "Hombre",
                "descripcion": "Ropa para hombre",
                "genero": "hombre",
                "hijos": [
                    {
                        "nombre": "Camisetas y camisas",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {
                                "nombre": "Camisas", 
                                "descripcion": "", 
                                "genero": "hombre",
                                "hijos":[
                                    {"nombre": "Camisas de cuadros", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisas vaqueras", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisas lisas", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisas estampadas", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisas de rayas", "descripcion": "", "genero": "hombre"},
                                ]
                            },
                            {
                                "nombre": "Camisetas", 
                                "descripcion": "", 
                                "genero": "hombre",
                                "hijos":[
                                    {"nombre": "Camisetas lisas", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisetas estampadas", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisetas de rayas", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisetas cuello redondo", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Camisetas cuello v", "descripcion": "", "genero": "hombre"},
                                ]
                            },
                            {"nombre": "Polos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Henley", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Camisetas sin mangas", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Vaqueros Hombre",
                        "descripcion": "Partes de abajo",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Vaqueros ajustados / Skinny", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Vaqueros rectos / Straight", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Vaqueros sueltos / Relaxed", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Vaqueros rotos", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Pantalones Hombre",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Chinos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Joggers", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pantalones pitillos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pantalones de pinzas / Vestir", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pantalones cargo", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Shorts Hombre",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Bermudas vaqueras", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Bermudas chinas", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Shorts de chándal", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Estilo cargo hombre", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Abrigos y Chaquetas Hombre",
                        "descripcion": "Prendas de exterior",
                        "genero": "hombre", 
                        "hijos": [
                            {
                                "nombre": "Abrigos",
                                "genero": "hombre",
                                "hijos": [
                                    {"nombre": "Trencas hombre", "genero": "hombre"},
                                    {"nombre": "Sobretodos", "genero": "hombre"},
                                    {"nombre": "Parkas hombre", "genero": "hombre"},
                                    {"nombre": "Chaquetones marineros", "genero": "hombre"},
                                    {"nombre": "Impermeables y Gabardinas", "genero": "hombre"},
                                ]
                            },
                            {"nombre": "Chalecos acolchados", "genero": "hombre"},
                            {
                                "nombre": "Chaquetas",
                                "genero": "hombre",
                                "hijos": [
                                    {"nombre": "Cazadoras bikers de cuero", "genero": "hombre"},
                                    {"nombre": "Chaquetas bombers", "genero": "hombre"},
                                    {"nombre": "Cazadoras vaqueras", "genero": "hombre"},
                                    {"nombre": "Chaquetas militares", "genero": "hombre"},
                                    {"nombre": "Forros polares", "genero": "hombre"},
                                    {"nombre": "Chaquetas harrington", "genero": "hombre"},
                                    {"nombre": "Plumíferos", "genero": "hombre"},
                                    {"nombre": "Sobrecamisas", "genero": "hombre"},
                                    {"nombre": "Cortavientos", "genero": "hombre"},
                                ]
                            },
                        ]
                    },
                    {
                        "nombre": "Jerséis y sudaderas Hombre",
                        "descripcion": "",
                        "genero": "hombre",
                        "hijos": [
                            {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "hombre"},
                            {
                                "nombre": "Jerséis", 
                                "descripcion": "Jerséis de punto", 
                                "genero": "hombre",
                                "hijos": [
                                    {"nombre": "Cuello alto", "descripcion": "Turtleneck", "genero": "hombre"},
                                    {"nombre": "Cuello de pico", "descripcion": "Escote en V", "genero": "hombre"},
                                    {"nombre": "Cuello redondo", "descripcion": "Crew neck", "genero": "hombre"},
                                    {"nombre": "Jerséis de punto grueso", "descripcion": "", "genero": "hombre"},
                                    {"nombre": "Cárdigans", "descripcion": "", "genero": "hombre"},
                                ]
                            },
                        ]
                    },
                    {
                        "nombre": "Trajes y blazers Hombre",
                        "descripcion": "",
                        "genero": "hombre",
                        "hijos": [
                            {"nombre": "Blazers y Americanas", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pantalones de traje", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Chalecos de traje", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Trajes completos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Trajes de boda / Esmoquin", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Ropa Interior Hombre",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Calzoncillos Slip", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Calzoncillos Boxer", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Camisetas interiores", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Calcetines", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Pijamas Hombre",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Pantalones de pijama", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pijamas completos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Albornoces y batas", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Ropa de baño Hombre",
                        "descripcion": "Playa y piscina",
                        "genero": "hombre",
                        "hijos": [
                            {"nombre": "Bañadores tipo short", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Bañadores slip", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {
                        "nombre": "Ropa deportiva Hombre",
                        "descripcion": "",
                        "genero": "hombre", 
                        "hijos": [
                            {"nombre": "Camisetas de entrenamiento", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Camisetas de equipos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Chándales completos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pantalones deportivos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Shorts deportivos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Sudaderas deportivas", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Chaquetas deportivas", "descripcion": "", "genero": "hombre"},
                        ]
                    }
                ]
            },
            {
                # ----------------------------------------------------------------------
                # ROPA NIÑAS
                # ----------------------------------------------------------------------
                "nombre": "Niñas",
                "descripcion": "Ropa para niñas",
                "genero": "niña",
                "hijos": [
                    {
                        "nombre": "Camisetas y tops", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Camisetas de manga corta", "descripcion": "", "genero": "niña"},
                            {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": "niña"},
                            {"nombre": "Blusas y camisas", "descripcion": "", "genero": "niña"},
                            {"nombre": "Tops de tirantes", "descripcion": "", "genero": "niña"},
                            {"nombre": "Tops deportivos", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Vestidos y faldas", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Vestidos de verano / casual", "descripcion": "", "genero": "niña"},
                            {"nombre": "Vestidos de fiesta / ceremonia", "descripcion": "", "genero": "niña"},
                            {"nombre": "Faldas vaqueras", "descripcion": "", "genero": "niña"},
                            {"nombre": "Faldas de tul", "descripcion": "", "genero": "niña"},
                            {"nombre": "Faldas pantalón", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Pantalones y vaqueros", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Vaqueros / Jeans", "descripcion": "", "genero": "niña"},
                            {"nombre": "Leggings", "descripcion": "", "genero": "niña"},
                            {"nombre": "Pantalones de chándal / Joggers", "descripcion": "", "genero": "niña"},
                            {"nombre": "Pantalones cortos / Shorts", "descripcion": "", "genero": "niña"},
                            {"nombre": "Monos y petos", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Jerséis y sudaderas", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "niña"},
                            {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "niña"},
                            {"nombre": "Jerséis de punto", "descripcion": "", "genero": "niña"},
                            {"nombre": "Cárdigans y chaquetas de punto", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Abrigos y chaquetas", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Abrigos y trencas", "descripcion": "", "genero": "niña"},
                            {"nombre": "Cazadoras de entretiempo", "descripcion": "", "genero": "niña"},
                            {"nombre": "Cazadoras vaqueras", "descripcion": "", "genero": "niña"},
                            {"nombre": "Plumíferos y acolchados", "descripcion": "", "genero": "niña"},
                            {"nombre": "Chalecos", "descripcion": "", "genero": "niña"},
                            {"nombre": "Chubasqueros / Impermeables", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Ropa de baño", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Bañadores", "descripcion": "", "genero": "niña"},
                            {"nombre": "Bikinis", "descripcion": "", "genero": "niña"},
                            {"nombre": "Culetines", "descripcion": "", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Ropa interior y pijamas", 
                        "descripcion": "", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Braguitas", "descripcion": "", "genero": "niña"},
                            {"nombre": "Camisetas interiores", "descripcion": "", "genero": "niña"},
                            {"nombre": "Calcetines y leotardos", "descripcion": "", "genero": "niña"},
                            {"nombre": "Pijamas de verano", "descripcion": "", "genero": "niña"},
                            {"nombre": "Pijamas de invierno", "descripcion": "", "genero": "niña"},
                            {"nombre": "Batas", "descripcion": "", "genero": "niña"}
                        ]
                    }
                ]
            },
            {
                # ----------------------------------------------------------------------
                # ROPA NIÑOS
                # ----------------------------------------------------------------------
                "nombre": "Niños",
                "descripcion": "Ropa para niños",
                "genero": "niño",
                "hijos": [
                    {
                        "nombre": "Camisetas y camisas", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Camisetas de manga corta", "descripcion": "", "genero": "niño"},
                            {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": "niño"},
                            {"nombre": "Polos", "descripcion": "", "genero": "niño"},
                            {"nombre": "Camisas casuales", "descripcion": "", "genero": "niño"},
                            {"nombre": "Camisas de vestir / ceremonia", "descripcion": "", "genero": "niño"}
                        ]
                    },
                    {
                        "nombre": "Pantalones y vaqueros", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Vaqueros / Jeans", "descripcion": "", "genero": "niño"},
                            {"nombre": "Pantalones chinos", "descripcion": "", "genero": "niño"},
                            {"nombre": "Pantalones de chándal / Joggers", "descripcion": "", "genero": "niño"},
                            {"nombre": "Bermudas y pantalones cortos", "descripcion": "", "genero": "niño"},
                            {"nombre": "Petos", "descripcion": "", "genero": "niño"}
                        ]
                    },
                    {
                        "nombre": "Jerséis y sudaderas", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "niño"},
                            {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "niño"},
                            {"nombre": "Jerséis de punto", "descripcion": "", "genero": "niño"},
                            {"nombre": "Cárdigans", "descripcion": "", "genero": "niño"}
                        ]
                    },
                    {
                        "nombre": "Abrigos y chaquetas", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Abrigos y trencas", "descripcion": "", "genero": "niño"},
                            {"nombre": "Cazadoras y chaquetas", "descripcion": "", "genero": "niño"},
                            {"nombre": "Cazadoras vaqueras", "descripcion": "", "genero": "niño"},
                            {"nombre": "Plumíferos y parkas", "descripcion": "", "genero": "niño"},
                            {"nombre": "Chalecos", "descripcion": "", "genero": "niño"},
                            {"nombre": "Cortavientos e impermeables", "descripcion": "", "genero": "niño"}
                        ]
                    },
                    {
                        "nombre": "Ropa de baño", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Bañadores tipo short", "descripcion": "", "genero": "niño"},
                            {"nombre": "Bañadores tipo slip", "descripcion": "", "genero": "niño"}
                        ]
                    },
                    {
                        "nombre": "Ropa interior y pijamas", 
                        "descripcion": "", 
                        "genero": "niño",
                        "hijos": [
                            {"nombre": "Calzoncillos (Slips y Boxers)", "descripcion": "", "genero": "niño"},
                            {"nombre": "Camisetas interiores", "descripcion": "", "genero": "niño"},
                            {"nombre": "Calcetines", "descripcion": "", "genero": "niño"},
                            {"nombre": "Pijamas de verano", "descripcion": "", "genero": "niño"},
                            {"nombre": "Pijamas de invierno", "descripcion": "", "genero": "niño"},
                            {"nombre": "Batas", "descripcion": "", "genero": "niño"}
                        ]
                    }
                ]
            },
            {
                # ----------------------------------------------------------------------
                # ROPA BEBÉS
                # ----------------------------------------------------------------------
                "nombre": "Bebés",
                "descripcion": "Ropa para bebés (0-36 meses)",
                "genero": "bebé",
                "hijos": [
                    {
                        "nombre": "Bodys y ropa interior", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Bodys manga corta", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Bodys manga larga", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Bodys de tirantes", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Peleles y ranitas", 
                        "descripcion": "Prendas de una sola pieza", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Peleles cortos / de verano", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Peleles largos / de invierno", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Ranitas y petos", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Conjuntos", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Conjuntos de algodón", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Conjuntos de punto", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Conjuntos de vestir / ceremonia", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Tops y jerséis", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Camisetas cruzadas", "descripcion": "Fáciles de poner", "genero": "bebé"},
                            {"nombre": "Camisetas normales", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Blusas y camisas", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Jerséis y chaquetas de punto", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Sudaderas", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Pantalones y braguitas", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Polainas", "descripcion": "Pantalones con pie incluido", "genero": "bebé"},
                            {"nombre": "Leggings infantiles", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Pantalones suaves", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Vaqueros de bebé", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Cubrepañales y braguitas", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Vestidos y faldas", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Vestidos casuales", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Vestidos de ceremonia", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Faldas", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Ropa de abrigo", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Buzos para nieve", "descripcion": "Cuerpo entero", "genero": "bebé"},
                            {"nombre": "Abrigos y chaquetones", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Cazadoras", "descripcion": "", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Pijamas y sacos de dormir", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Pijamas de cuerpo entero (enterizos)", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Pijamas de dos piezas", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Sacos de dormir", "descripcion": "Para la cuna", "genero": "bebé"}
                        ]
                    },
                    {
                        "nombre": "Ropa de baño", 
                        "descripcion": "", 
                        "genero": "bebé",
                        "hijos": [
                            {"nombre": "Bañadores pañal", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Bañadores y bikinis", "descripcion": "", "genero": "bebé"},
                            {"nombre": "Camisetas de protección solar UV", "descripcion": "", "genero": "bebé"}
                        ]
                    }
                ]
            },
            {
                # ----------------------------------------------------------------------
                # OTROS (Unisex o generales)
                # ----------------------------------------------------------------------
                "nombre": "Disfraces y trajes especiales",
                "descripcion": "",
                "genero": "",
            },
            {
                "nombre": "Otras prendas",
                "descripcion": "",
                "genero": "",
            }
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
                "nombre": "Mujer", "genero": "mujer", "hijos": [
                    {"nombre": "Zapatillas y deportivas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Botas altas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Botines", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Zapatos de tacón", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Zapatos planos / Bailarinas", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Sandalias", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Botas de agua", "descripcion": "", "genero": "mujer"}
                ]
            },
            {
                "nombre": "Hombre", "genero": "hombre", "hijos": [
                    {"nombre": "Zapatillas y deportivas", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Botas y botines", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Zapatos formales / Oxford", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Mocasines y Náuticos", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Sandalias y chanclas", "descripcion": "", "genero": "hombre"}
                ]
            },
            {
                "nombre": "Niña", "genero": "niña", "hijos": [
                    {"nombre": "Zapatillas y deportivas niña", "descripcion": "", "genero": "niña"},
                    {"nombre": "Botas y botines niña", "descripcion": "", "genero": "niña"},
                    {"nombre": "Bailarinas y manoletinas", "descripcion": "", "genero": "niña"},
                    {"nombre": "Sandalias niña", "descripcion": "", "genero": "niña"},
                    {"nombre": "Zapatos colegiales niña", "descripcion": "", "genero": "niña"}
                ]
            },
            {
                "nombre": "Niño", "genero": "niño", "hijos": [
                    {"nombre": "Zapatillas y deportivas niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Botas y botines niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Zapatos de vestir niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Sandalias niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Zapatos colegiales niño", "descripcion": "", "genero": "niño"}
                ]
            },
            {
                "nombre": "Bebé", "genero": "bebé", "hijos": [
                    {"nombre": "Patucos", "descripcion": "Para recién nacidos", "genero": "bebé"},
                    {"nombre": "Badanas y sin suela", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Zapatos primeros pasos", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Deportivas bebé", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Botitas bebé", "descripcion": "", "genero": "bebé"}
                ]
            }
        ]
    },
    {
        # ==============================================================================
        # 3. BOLSOS (Principalmente Mujer/Unisex, lo dejamos plano)
        # ==============================================================================
        "nombre": "Bolsos",
        "descripcion": "Bolsos, mochilas y maletas",
        "genero": "",
        "hijos":[
            {"nombre": "Mochilas", "descripcion": "", "genero": ""},
            {"nombre": "Bolsas de playa", "descripcion": "", "genero": "mujer"},
            {"nombre": "Maletines", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos cubo", "descripcion": "", "genero": "mujer"},
            {"nombre": "Riñoneras", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos de fiesta", "descripcion": "", "genero": "mujer"},
            {"nombre": "Portatrajes", "descripcion": "", "genero": ""},
            {"nombre": "Bolsas de deporte", "descripcion": "", "genero": ""},
            {"nombre": "Bolsos de mano", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos boho", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsas de viaje", "descripcion": "", "genero": ""},
            {"nombre": "Maletas", "descripcion": "", "genero": ""},
            {"nombre": "Neceseres", "descripcion": "", "genero": ""},
            {"nombre": "Satchels", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos de hombro", "descripcion": "", "genero": "mujer"},
            {"nombre": "Bolsos tote", "descripcion": "", "genero": "mujer"},
            {"nombre": "Monederos y carteras", "descripcion": "", "genero": ""},
        ]
    },
    {
        # ==============================================================================
        # 4. ACCESORIOS
        # ==============================================================================
        "nombre": "Accesorios",
        "descripcion": "Complementos de moda",
        "genero": "",
        "hijos": [
            {
                "nombre": "Mujer", "genero": "mujer", "hijos": [
                    {
                        "nombre": "Joyeria", 
                        "descripcion": "Collares, anillos, pulseras", 
                        "genero": "mujer",
                        "hijos": [
                            {"nombre": "Anillos", "descripcion": "Anillos y sortijas", "genero": "mujer"},
                            {"nombre": "Pendientes", "descripcion": "Aros, largos, botón", "genero": "mujer"},
                            {"nombre": "Collares y colgantes", "descripcion": "Gargantillas, cadenas", "genero": "mujer"},
                            {"nombre": "Pulseras y brazaletes", "descripcion": "Esclavas, pulseras de cadena", "genero": "mujer"},
                            {"nombre": "Tobilleras", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Broches", "descripcion": "", "genero": "mujer"},
                            {"nombre": "Conjuntos de joyería", "descripcion": "", "genero": "mujer"},
                        ]
                    },
                    {"nombre": "Bandanas y pañuelos para el pelo", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Cinturones", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Sombreros y gorros", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Gafas de sol", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Bufandas y pañuelos", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Accesorios de cabello", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Relojes", "descripcion": "", "genero": "mujer"},
                    {"nombre": "Guantes", "descripcion": "", "genero": "mujer"}
                ]
            },
            {
                "nombre": "Hombre", "genero": "hombre", "hijos": [
                    {
                        "nombre": "Joyeria", 
                        "descripcion": "Pulseras, anillos, gemelos", 
                        "genero": "hombre",
                        "hijos": [
                            {"nombre": "Anillos y sellos", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pulseras", "descripcion": "De cuero, acero, plata", "genero": "hombre"},
                            {"nombre": "Collares y cadenas", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Pendientes", "descripcion": "", "genero": "hombre"},
                            {"nombre": "Gemelos", "descripcion": "Para camisas", "genero": "hombre"},
                            {"nombre": "Pasadores de corbata", "descripcion": "", "genero": "hombre"},
                        ]
                    },
                    {"nombre": "Cinturones", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Sombreros y gorras", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Gafas de sol", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Bufandas", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Corbatas y pajaritas", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Relojes", "descripcion": "", "genero": "hombre"},
                    {"nombre": "Guantes", "descripcion": "", "genero": "hombre"},
                ]
            },
            {
                {
                "nombre": "Niña", "genero": "niña", "hijos": [
                    {
                        "nombre": "Accesorios para el pelo", 
                        "descripcion": "Adornos para el cabello", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Diademas", "genero": "niña"},
                            {"nombre": "Lazos y moñas", "genero": "niña"},
                            {"nombre": "Horquillas y clips", "genero": "niña"},
                            {"nombre": "Coleteros y elásticos", "genero": "niña"},
                            {"nombre": "Coronas de flores", "genero": "niña"}
                        ]
                    },
                    {
                        "nombre": "Bisutería Infantil", 
                        "descripcion": "Joyas para niñas", 
                        "genero": "niña",
                        "hijos": [
                            {"nombre": "Collares", "genero": "niña"},
                            {"nombre": "Pulseras", "genero": "niña"},
                            {"nombre": "Anillos infantiles", "genero": "niña"},
                            {"nombre": "Pendientes / Arracadas", "genero": "niña"}
                        ]
                    },
                    {"nombre": "Bufandas, guantes y orejeras", "descripcion": "", "genero": "niña"},
                    {"nombre": "Gorros y sombreros", "descripcion": "", "genero": "niña"},
                    {"nombre": "Gafas de sol", "descripcion": "", "genero": "niña"},
                    {"nombre": "Cinturones", "descripcion": "", "genero": "niña"},
                    {"nombre": "Mochilas y bolsos", "descripcion": "Mochilas escolares y bolsitos", "genero": "niña"},
                    {"nombre": "Relojes infantiles", "descripcion": "", "genero": "niña"},
                    {"nombre": "Paraguas e impermeables", "descripcion": "", "genero": "niña"}
                ]
                },
            },
            {
                "nombre": "Niño", "genero": "niño", "hijos": [
                    {"nombre": "Gorras y sombreros niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Cinturones niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Bufandas y guantes niño", "descripcion": "", "genero": "niño"},
                    {"nombre": "Mochilas infantiles niño", "descripcion": "", "genero": "niño"}
                ]
            },
            {
                "nombre": "Bebé", "genero": "bebé", "hijos": [
                    {"nombre": "Baberos y bandanas", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Muselinas y gasas", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Arrullos y mantas", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Gorritos bebé", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Manoplas antiarañazos", "descripcion": "", "genero": "bebé"},
                    {"nombre": "Lazos y diademas bebé", "descripcion": "", "genero": "bebé"}
                ]
            },
            {
                "nombre": "Unisex / Otros", "genero": "", "hijos": [
                    {"nombre": "Paraguas", "descripcion": "", "genero": ""},
                    {"nombre": "Llaveros", "descripcion": "", "genero": ""},
                ]
            }
        ]
    }
]

# ==============================================================================
# 2. LÓGICA DE SINCRONIZACIÓN (UPSERT)
# ==============================================================================

def sincronizar_recursivo(db: Session, nodo: dict, parent_id: int = None):
    nombre = nodo["nombre"]
    
    if nombre.lower() == "todos":
        return

    genero_valor = nodo.get("genero")
    if genero_valor == "": 
        genero_valor = None 

    categoria = db.query(Categoria).filter(
        Categoria.nombre == nombre,
        Categoria.parent_id == parent_id
    ).first()

    if categoria:
        # Actualizamos género, descripción y ASEGURAMOS que esté activa (por si se había borrado lógicamente)
        categoria.genero = genero_valor
        categoria.descripcion = nodo.get("descripcion", "")
        categoria.activo = True # 👈 Aseguramos que vuelva a estar visible
        db.flush()
        print(f"🔄 Sincronizada: {nombre}")
    else:
        # Creamos la categoría nueva
        categoria = Categoria(
            nombre=nombre,
            descripcion=nodo.get("descripcion", ""),
            genero=genero_valor,
            parent_id=parent_id,
            activo=True # 👈 La creamos activa por defecto
        )
        db.add(categoria)
        db.flush()
        print(f"✨ Creada: {nombre}")

    for hijo in nodo.get("hijos", []):
        sincronizar_recursivo(db, hijo, parent_id=categoria.id)

def poblar_categorias():
    db = SessionLocal()
    try:
        print("🚀 Iniciando sincronización de categorías...")
        for cat in categorias_master:
            sincronizar_recursivo(db, cat)
            
        db.commit()
        print("✅ Categorías actualizadas correctamente.")
    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la sincronización: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    poblar_categorias()










































































































































# from sqlalchemy.orm import Session
# from app.db.database import SessionLocal, engine, Base

# # Importar modelos
# # from app.models.categorias_model import Categoria
# # from app.models.producto_model import Producto


# from app.models.categorias_model import Categoria
# from app.models.producto_model import Producto
# from app.models.marcas_model import Marca
# from app.models.variantes_model import Variante
# from app.models.variante_imagen_model import Imagen
# from app.models.ventas_model import Venta
# from app.models.atributo_model import Atributo, ValorAtributo
# from app.models.stock_model import Stock
# from app.models.proveedores_model import Proveedor



# # ==============================================================================
# # 1. DATOS MAESTROS (Estructura Plana y Unificada)
# # ==============================================================================

# categorias_master = [
#     {
#         # ==============================================================================
#         # 1. ROPA
#         # ==============================================================================
#         "nombre": "Ropa",
#         "descripcion": "Ropa general",
#         "genero": "", 
#         "hijos": [
#             {
#                 # FALDAS
#                 "nombre": "Faldas", 
#                 "descripcion": "Minifaldas, midi, largas",
#                 "genero": "mujer",
#                 "hijos": [
#                     {"nombre": "Minifaldas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Faldas por la rodilla", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Faldas midi", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Faldas largas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Faldas asimétricas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Falda-pantalón", "descripcion": "", "genero": "mujer"},
#                 ]
#             },
#             {
#                 # VESTIDOS
#                 "nombre": "Vestidos",
#                 "genero": "mujer",
#                 "hijos": [
                    
#                     {"nombre": "Vestidos cortos / Mini", "genero": "mujer"},
#                     {"nombre": "Vestidos midi", "genero": "mujer"},
#                     {"nombre": "Vestidos largos / Maxi", "genero": "mujer"},
#                     {"nombre": "Vestidos vaqueros", "genero": "mujer"},
#                     {"nombre": "Vestidos de punto", "genero": "mujer"},
#                     {"nombre": "Vestidos camiseros", "genero": "mujer"},
#                     {"nombre": "Vestidos formales", "genero": "mujer"},
#                     {"nombre": "Vestidos informales", "genero": "mujer"},
#                     {"nombre": "Vestidos sin tirantes", "genero": "mujer"},
#                     {"nombre": "Vestidos negros", "genero": "mujer"},
#                     {"nombre": "Vestidos de verano / Playeros", "genero": "mujer"},
#                     {"nombre": "Vestidos de invierno", "genero": "mujer"},
#                     {
#                         "nombre": "Ocasiones especiales",
#                         "genero": "mujer",
#                         "hijos": [
#                             {"nombre": "Vestidos de fiesta y cóctel", "genero": "mujer"},
#                             {"nombre": "Vestidos de novia", "genero": "mujer"},
#                             {"nombre": "Vestidos de graduación", "genero": "mujer"},
#                             {"nombre": "Vestidos de noche", "genero": "mujer"},
#                             {"nombre": "Espalda descubierta", "genero": "mujer"},
#                         ]
#                     },
#                     {"nombre": "Otros vestidos", "genero": "mujer"},
#                 ]
#             },
#             {
#                 # CAMISETAS Y TOPS
#                 "nombre": "Camisetas y tops",
#                 "descripcion": "Camisas, blusas, tops",
#                 "genero": "mujer",
#                 "hijos": [
#                     {"nombre": "Camisas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "blusas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "chalecos", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Camisetas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Sin mangas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Túnicas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Crop tops", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Manga corta", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Manga 3/4", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Manga Larga", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Bodies", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Hombros descubiertos", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Cuello alto", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Peplum", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Halter", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Otros tops", "descripcion": "", "genero": "mujer"},
#                 ]
#             },
#             {
#                 # CAMISETAS Y CAMISAS
#                 "nombre": "Camisetas y camisas",
#                 "descripcion": "",
#                 "genero": "hombre", 
#                 "hijos": [
#                     {
#                         "nombre": "Camisas", 
#                         "descripcion": "", 
#                         "genero": "",
#                         "hijos":[
#                             {"nombre": "Camisas de cuadros", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisas vaqueras", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisas lisas", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisas estampadas", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisas de rayas", "descripcion": "", "genero": ""},
#                             {"nombre": "Otras camisetas", "descripcion": "", "genero": ""},
#                         ]
#                     },
#                     {
#                         "nombre": "camisetas", 
#                         "descripcion": "", 
#                         "genero": "",
#                         "hijos":[
#                             {"nombre": "Camisetas lisas", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisetas estampadas", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisetas de rayas", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisetas cuello redondo", "descripcion": "", "genero": ""},
#                             {"nombre": "Camisetas cuello v", "descripcion": "", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Polos", "descripcion": "", "genero": ""},
#                     {"nombre": "Henley", "descripcion": "", "genero": ""},
#                     {"nombre": "Camisetas sin mangas", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},
#                 ]
#             },
#                 #FALDA PANTALON
#             {"nombre": "Falda pantalon", "descripcion": "", "genero": "mujer"},
#             {
#                 # VAQUEROS
#                 "nombre": "Vaqueros",
#                 "descripcion": "Partes de abajo",
#                 "genero": "", 
#                 "hijos": [
#                     {"nombre": "Vaqueros boyfriend", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Vaqueros tobilleros", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Vaqueros de campana", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros de cintura alta", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros rotos", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros pitillo", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros rectos", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros ajustados", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Otros Vaqueros", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # PANTALONES Y LEGGGINS
#                 "nombre": "Pantalones y leggins",
#                 "descripcion": "",
#                 "genero": "mujer", 
#                 "hijos": [
#                     {"nombre": "Pantalones tobilleros y chinos", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones anchos", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones ptitillo", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones de pinzas", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones rectos", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones de cuero", "descripcion": "", "genero": ""},
#                     {"nombre": "Leggins", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones harén", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros Pantalones", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # PANTALONES
#                 "nombre": "Pantalones",
#                 "descripcion": "",
#                 "genero": "", 
#                 "hijos": [
#                     {"nombre": "Chinos", "descripcion": "", "genero": ""},
#                     {"nombre": "Joggers", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones pitillos", "descripcion": "", "genero": ""},
#                     {"nombre": "Capri", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones de pinzas", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones anchos", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # SHORTS
#                 "nombre": "Shorts",
#                 "descripcion": "",
#                 "genero": "", 
#                 "hijos": [
#                     {"nombre": "De cintura baja", "descripcion": "", "genero": ""},
#                     {"nombre": "De cintura alta", "descripcion": "", "genero": ""},
#                     {"nombre": "Hasta la rodilla", "descripcion": "", "genero": ""},
#                     {"nombre": "Vaqueros", "descripcion": "", "genero": ""},
#                     {"nombre": "De encaje", "descripcion": "", "genero": ""},
#                     {"nombre": "De cuero", "descripcion": "", "genero": ""},
#                     {"nombre": "Estilo cargo", "descripcion": "", "genero": ""},
#                     {"nombre": "Capri", "descripcion": "", "genero": ""},
#                     {"nombre": "Chinos", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Estilo cargo", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Otros shorts", "descripcion": "", "genero": ""},
                    
#                 ]
#             },
#             {
#                 #  MONOS
#                 "nombre": "",
#                 "descripcion": "",
#                 "genero": "mujer", 
#                 "hijos": [
#                     {"nombre": "Monos largos", "descripcion": "", "genero": ""},
#                     {"nombre": "Monos cortos", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros monos", "descripcion": "", "genero": ""},
                    
#                 ]
#             },
#             {
#                 # ABRIGOS
#                 "nombre": "Abrigos y Chaquetas",
#                 "descripcion": "Prendas de exterior y abrigo",
#                 "genero": "", 
#                 "hijos": [
#                     {
#                         "nombre": "Abrigos",
#                         "genero": "",
#                         "hijos": [
#                             {"nombre": "Trencas", "genero": ""},
#                             {"nombre": "Sobretodos y abrigos largos", "genero": ""},
#                             {"nombre": "Parkas", "genero": ""},
#                             {"nombre": "Chaquetones marineros", "genero": ""},
#                             {"nombre": "Impermeables", "genero": ""},
#                             {"nombre": "Gabardinas", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Chalecos", "genero": ""},
#                     {
#                         "nombre": "Chaquetas",
#                         "genero": "",
#                         "hijos": [
#                             {"nombre": "Cazadoras bikers", "genero": ""},
#                             {"nombre": "Chaquetas bombers", "genero": ""},
#                             {"nombre": "Cazadoras vaqueras", "genero": ""},
#                             {"nombre": "Chaquetas militares y utilitarias", "genero": ""},
#                             {"nombre": "Forros polares", "genero": ""},
#                             {"nombre": "Chaquetas harrington", "genero": ""},
#                             {"nombre": "Chaquetas de plumas", "genero": ""},
#                             {"nombre": "Chaquetas acolchadas", "genero": ""},
#                             {"nombre": "Sobrecamisas", "genero": ""},
#                             {"nombre": "Chaquetas de esquí y snow", "genero": ""},
#                             {"nombre": "Chaquetas universitarias", "genero": ""},
#                             {"nombre": "Cortavientos", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Ponchos", "genero": ""},
#                 ]
#             },
#             {
#                 # SUDADERAS
#                 "nombre": "Jerséis y sudaderas",
#                 "descripcion": "",
#                 "genero": "",
#                 "hijos": [
#                     {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": ""},
#                     {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": ""},
#                     {
#                         "nombre": "Jerséis", 
#                         "descripcion": "Jerséis de punto", 
#                         "genero": "",
#                         "hijos": [
#                             {"nombre": "Cuello alto", "descripcion": "Turtleneck", "genero": ""},
#                             {"nombre": "Cuello de pico", "descripcion": "Escote en V", "genero": ""},
#                             {"nombre": "Cuello redondo", "descripcion": "Crew neck", "genero": ""},
#                             {"nombre": "Jerséis largos", "descripcion": "Tipo túnica o oversize", "genero": "mujer"},
#                             {"nombre": "Jerséis de punto fino", "descripcion": "", "genero": ""},
#                             {"nombre": "Jerséis de punto grueso", "descripcion": "", "genero": ""},
#                             {"nombre": "Manga 3/4", "descripcion": "", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Kimonos", "descripcion": "", "genero": ""},
#                     {"nombre": "Cárdigan", "descripcion": "", "genero": ""},
#                     {"nombre": "Boleros", "descripcion": "", "genero": ""},
#                     {"nombre": "Chalecos", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros jerséis y sudaderas", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # TRAJES
#                 "nombre": "Trajes y blazers",
#                 "descripcion": "",
#                 "genero": "",
#                 "hijos": [
#                     {"nombre": "Blazers", "descripcion": "", "genero": ""},
#                     {"nombre": "Trajes de pantalón", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones de trajes", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Chalecos", "descripcion": "", "genero": ""},
#                     {"nombre": "Trajes", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Trajes de boda", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Trajes de falda", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Piezas de traje", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros trajes y blazers", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # ROPA INTERIOR
#                 "nombre": "Ropa Interior",
#                 "descripcion": "",
#                 "genero": "hombre", 
#                 "hijos": [
#                     {"nombre": "Calzoncillos", "descripcion": "", "genero": ""},
#                     {"nombre": "Calcetines", "descripcion": "", "genero": ""},
#                     {"nombre": "Albornoces", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # ROPA DE BAÑO
#                 "nombre": "Ropa de baño",
#                 "descripcion": "Playa y piscina",
#                 "genero": "mujer",
#                 "hijos": [
#                     {"nombre": "Bikinis", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Bañadores", "descripcion": "Una pieza o short", "genero": ""},
#                     {"nombre": "Trikinis", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Pareos y caftanes", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Otros", "descripcion": "", "genero": "mujer"},
#                 ]
#             },
#                 # BAÑADORES 
#             {"nombre": "Bañadores", "descripcion": "", "genero": "mujer"},
#             {
#                 # LENCERIAS Y PIJAMAS
#                 "nombre": "Lencería y pijamas",
#                 "descripcion": "",
#                 "genero": "mujer", 
#                 "hijos": [
#                     {"nombre": "Sujetadores", "descripcion": "", "genero": ""},
#                     {"nombre": "Braguitas", "descripcion": "", "genero": ""},
#                     {"nombre": "Conjuntos", "descripcion": "", "genero": ""},
#                     {"nombre": "Lencería moldeadora", "descripcion": "", "genero": ""},
#                     {"nombre": "Pijamas", "descripcion": "", "genero": ""},
#                     {"nombre": "Batas", "descripcion": "", "genero": ""},
#                     {"nombre": "Medias", "descripcion": "", "genero": ""},
#                     {"nombre": "Calcetines", "descripcion": "", "genero": ""},
#                     {"nombre": "Accersorios de lencería", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # PIJAMAS
#                 "nombre": "Pijamas",
#                 "descripcion": "",
#                 "genero": "hombre", 
#                 "hijos": [
#                     {"nombre": "Pijama de una sola pieza", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones de pijama", "descripcion": "", "genero": ""},
#                     {"nombre": "Pijamas completos", "descripcion": "", "genero": ""},
#                     {"nombre": "Camisetas de pijama", "descripcion": "", "genero": ""},
#                     {"nombre": "otros", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 # PREMAMA
#                 "nombre": "Premamá",
#                 "descripcion": "",
#                 "genero": "mujer", 
#                 "hijos": [
#                     {"nombre": "Camisetas y blusas", "descripcion": "", "genero": ""},
#                     {"nombre": "Vestidos", "descripcion": "", "genero": ""},
#                     {"nombre": "Faldas", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones", "descripcion": "", "genero": ""},
#                     {"nombre": "Shorts", "descripcion": "", "genero": ""},
#                     {"nombre": "Monos", "descripcion": "", "genero": ""},
#                     {"nombre": "Sudaderas y jerseís", "descripcion": "", "genero": ""},
#                     {"nombre": "Abrigos y cazadoras", "descripcion": "", "genero": ""},
#                     {"nombre": "Bañadores y pareos", "descripcion": "", "genero": ""},
#                     {
#                         "nombre": "Ropa interior", 
#                         "descripcion": "", 
#                         "genero": "",
#                         "hijos":[
#                             {"nombre": "Ropa interior", "descripcion": "", "genero": ""},
#                             {"nombre": "Pijamas", "descripcion": "", "genero": ""},
#                             {"nombre": "sujetadores premamá y posparto", "descripcion": "", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Ropa de deporte", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},

                    
#                 ]
#             },
#             {
#                 # ROPA DEPORTIVA
#                 "nombre": "Ropa deportiva",
#                 "descripcion": "",
#                 "genero": "", 
#                 "hijos": [
#                     {"nombre": "Ropa de abrigo", "descripcion": "", "genero": ""},
#                     {"nombre": "Ropa de entrenamiento", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Chándales", "descripcion": "", "genero": ""},
#                     {"nombre": "Pantalones", "descripcion": "", "genero": ""},
#                     {"nombre": "Shorts", "descripcion": "", "genero": ""},
#                     {"nombre": "Vestidos", "descripcion": "", "genero": ""},
#                     {"nombre": "Faldas", "descripcion": "", "genero": ""},
#                     {"nombre": "Tops y camisetas", "descripcion": "", "genero": ""},
#                     {"nombre": "Camisetas de equipos", "descripcion": "", "genero": ""},
#                     {"nombre": "Sudaderas", "descripcion": "", "genero": ""},
#                     {"nombre": "Sudaderas y suéteres", "descripcion": "", "genero": "hombre"},
#                     {
#                         "nombre": "Accesorios", 
#                         "descripcion": "", 
#                         "genero": "",
#                         "hijos":[
#                             {"nombre": "Gafas", "descripcion": "", "genero": ""},
#                             {"nombre": "Guantes", "descripcion": "", "genero": ""},
#                             {"nombre": "Gorras", "descripcion": "", "genero": ""},
#                             {"nombre": "Bufandas", "descripcion": "", "genero": ""},
#                             {"nombre": "Muñequeras", "descripcion": "", "genero": ""},
#                         ]
#                     },
#                     {"nombre": "Sujetadores", "descripcion": "", "genero": ""},
#                     {"nombre": "Otros", "descripcion": "", "genero": ""},
                    
#                 ]
#             },
#             {
#                 # DISFRACES Y TRAJES ESPECIALES
#                 "nombre": "Disfraces y trajes especiales",
#                 "descripcion": "",
#                 "genero": "",
#             },
#             {
#                 # OTRAS PRENDAS
#                 "nombre": "Otras prendas",
#                 "descripcion": "",
#                 "genero": "",
#             },
#         ]
#     },
#     {
#         # ==============================================================================
#         # 2. CALZADO
#         # ==============================================================================
#         "nombre": "Calzado",
#         "descripcion": "Zapatos y zapatillas",
#         "genero": "",
#         "hijos": [
#             {
#                 "nombre": "Zapatillas", 
#                 "descripcion": "Sneakers y deportivas", 
#                 "genero": "",
#                 "hijos": [
#                     {"nombre": "Running", "descripcion": "", "genero": ""},
#                     {"nombre": "Casual / Lona", "descripcion": "", "genero": ""},
#                     {"nombre": "Futbol", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 "nombre": "Botas y Botines", 
#                 "descripcion": "", 
#                 "genero": "",
#                 "hijos": [
#                     {"nombre": "Botas altas", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Botines", "descripcion": "", "genero": ""},
#                     {"nombre": "Botas de agua", "descripcion": "", "genero": ""},
#                     {"nombre": "Botas militares", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 "nombre": "Zapatos formales", 
#                 "descripcion": "", 
#                 "genero": "",
#                 "hijos": [
#                     {"nombre": "Tacones", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Mocasines", "descripcion": "", "genero": ""},
#                     {"nombre": "Oxford / Derby", "descripcion": "", "genero": "hombre"},
#                     {"nombre": "Alpargatas", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {
#                 "nombre": "Sandalias", 
#                 "descripcion": "", 
#                 "genero": "",
#                  "hijos": [
#                     {"nombre": "Sandalias planas", "descripcion": "", "genero": ""},
#                     {"nombre": "Sandalias de tacón", "descripcion": "", "genero": "mujer"},
#                     {"nombre": "Chanclas", "descripcion": "", "genero": ""},
#                  ]
#             }
#         ]
#     },
#     {
#         # ==============================================================================
#         # 3. BOLSOS
#         # ==============================================================================
#         "nombre": "Bolsos",
#         "descripcion": "",
#         "genero": "",
#         "hijos":[
#             {"nombre": "Mochilas", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsas de playa", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Maletines", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsos cubo", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Riñoneras", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsos de fiesta", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Portatrajes", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsa de deporte, Bolso de deporte, bolsa de gimnasio", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsos de mano", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Bolsos boho", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Bolsas de viaje", "descripcion": "", "genero": ""},
#             {"nombre": "Maletas", "descripcion": "", "genero": ""},
#             {"nombre": "Neceseres", "descripcion": "", "genero": ""},
#             {"nombre": "Satchels", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Bolsos de hombro", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Bolsos tote", "descripcion": "", "genero": "mujer"},
#             {"nombre": "Monederos y carteras", "descripcion": "", "genero": ""},
#             {"nombre": "Bolsos de pulseras", "descripcion": "", "genero": "mujer"}
#         ]
#     },
#     {
#         # ==============================================================================
#         # 4. Accesorios
#         # ==============================================================================
#         "nombre": "Accesorios",
#         "descripcion": "",
#         "genero": "",
#         "hijos": [
#             {"nombre": "Bandanas y pañuelos para el pelo", "descripcion": "", "genero": ""},
#             {"nombre": "Cinturones", "descripcion": "", "genero": ""},
#             {"nombre": "Guantes", "descripcion": "", "genero": ""},
#             {"nombre": "Accesorios de cabello", "descripcion": "", "genero": ""},
#             {"nombre": "Pañuelos", "descripcion": "", "genero": ""},
#             {"nombre": "Sombreros y gorros", 
#              "descripcion": "", 
#              "genero": "",
#              "hijos": [
#                 {"nombre": "Pasamontañas", "descripcion": "", "genero": ""},
#                 {"nombre": "Gorros de lana", "descripcion": "", "genero": ""},
#                 {"nombre": "Gorros", "descripcion": "", "genero": ""},
#                 {"nombre": "Orejeras", "descripcion": "", "genero": ""},
#                 {"nombre": "Tocados", "descripcion": "", "genero": ""},
#                 {"nombre": "Sombreros", "descripcion": "", "genero": ""},
#                 {"nombre": "Diademas y cintas", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {"nombre": "Joyeria", 
#              "descripcion": "", 
#              "genero": "",
#              "hijos": [
#                 {"nombre": "Tobilleras", "descripcion": "", "genero": ""},
#                 {"nombre": "Joyas corporales", "descripcion": "", "genero": ""},
#                 {"nombre": "Pulsares", "descripcion": "", "genero": ""},
#                 {"nombre": "Broches", "descripcion": "", "genero": ""},
#                 {"nombre": "Colgantes y dijes", "descripcion": "", "genero": ""},
#                 {"nombre": "Pendientes", "descripcion": "", "genero": ""},
#                 {"nombre": "Conjuntos de joyería", "descripcion": "", "genero": ""},
#                 {"nombre": "Collares", "descripcion": "", "genero": ""},
#                 {"nombre": "Anillos", "descripcion": "", "genero": ""},
#                 ]
#             },
#             {"nombre": "Llaveros", "descripcion": "", "genero": ""},
#             {"nombre": "Bufandas y pañuelos", "descripcion": "", "genero": ""},
#             {"nombre": "Gafas de sol", "descripcion": "", "genero": ""},
#             {"nombre": "Paraguas", "descripcion": "", "genero": ""},
#             {"nombre": "Relojes", "descripcion": "", "genero": ""},
#         ]
#     },
#     {
#         # ==============================================================================
#         # 5. NIÑOS Y BEBÉS
#         # ==============================================================================
#         "nombre": "Niños y Bebés",
#         "descripcion": "Moda infantil, calzado y accesorios desde 0 meses hasta 14+ años",
#         "genero": "", 
#         "hijos": [
#             {
#                 # ----------------------------------------------------------------------
#                 # NIÑAS
#                 # ----------------------------------------------------------------------
#                 "nombre": "Niñas",
#                 "descripcion": "Ropa, calzado y accesorios para niñas",
#                 "genero": "niña",
#                 "hijos": [
#                     {
#                         "nombre": "Camisetas y tops", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Camisetas de manga corta", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Blusas y camisas", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Tops de tirantes", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Tops deportivos", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Vestidos y faldas", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Vestidos de verano / casual", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Vestidos de fiesta / ceremonia", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Faldas vaqueras", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Faldas de tul", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Faldas pantalón", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Pantalones y vaqueros", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Vaqueros / Jeans", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Leggings", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Pantalones de chándal / Joggers", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Pantalones cortos / Shorts", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Monos y petos", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Jerséis y sudaderas", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Jerséis de punto", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Cárdigans y chaquetas de punto", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Abrigos y chaquetas", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Abrigos y trencas", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Cazadoras y chaquetas de entretiempo", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Cazadoras vaqueras", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Plumíferos y acolchados", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Chalecos", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Chubasqueros / Impermeables", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa de baño", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Bañadores", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Bikinis", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Culetines", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa interior y pijamas", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Braguitas", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Camisetas interiores", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Calcetines y leotardos", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Pijamas de verano", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Pijamas de invierno", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Batas", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {
#                         "nombre": "Calzado niña", 
#                         "descripcion": "", 
#                         "genero": "niña",
#                         "hijos": [
#                             {"nombre": "Zapatillas y deportivas", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Botas y botines", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Bailarinas y manoletinas", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Sandalias", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Zapatos colegiales", "descripcion": "", "genero": "niña"},
#                             {"nombre": "Zapatillas de casa", "descripcion": "", "genero": "niña"}
#                         ]
#                     },
#                     {"nombre": "Accesorios niña", "descripcion": "Diademas, lazos, bufandas, mochilas", "genero": "niña"}
#                 ]
#             },
#             {
#                 # ----------------------------------------------------------------------
#                 # NIÑOS
#                 # ----------------------------------------------------------------------
#                 "nombre": "Niños",
#                 "descripcion": "Ropa, calzado y accesorios para niños",
#                 "genero": "niño",
#                 "hijos": [
#                     {
#                         "nombre": "Camisetas y camisas", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Camisetas de manga corta", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Polos", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Camisas casuales", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Camisas de vestir / ceremonia", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Pantalones y vaqueros", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Vaqueros / Jeans", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Pantalones chinos / de vestir", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Pantalones de chándal / Joggers", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Bermudas y pantalones cortos", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Petos", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Jerséis y sudaderas", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Jerséis de punto", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Cárdigans", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Abrigos y chaquetas", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Abrigos y trencas", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Cazadoras y chaquetas", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Cazadoras vaqueras", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Plumíferos y parkas", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Chalecos", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Cortavientos e impermeables", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa de baño", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Bañadores tipo short", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Bañadores tipo slip", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa interior y pijamas", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Calzoncillos (Slips y Boxers)", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Camisetas interiores", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Calcetines", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Pijamas de verano", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Pijamas de invierno", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Batas", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {
#                         "nombre": "Calzado niño", 
#                         "descripcion": "", 
#                         "genero": "niño",
#                         "hijos": [
#                             {"nombre": "Zapatillas y deportivas", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Botas y botines", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Zapatos de vestir / Mocasines", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Zapatos colegiales", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Sandalias", "descripcion": "", "genero": "niño"},
#                             {"nombre": "Zapatillas de casa", "descripcion": "", "genero": "niño"}
#                         ]
#                     },
#                     {"nombre": "Accesorios niño", "descripcion": "Gorras, cinturones, bufandas, mochilas", "genero": "niño"}
#                 ]
#             },
#             {
#                 # ----------------------------------------------------------------------
#                 # BEBÉS (0-36 Meses)
#                 # ----------------------------------------------------------------------
#                 "nombre": "Bebés",
#                 "descripcion": "Ropa y accesorios para bebés (0-36 meses)",
#                 "genero": "bebé",
#                 "hijos": [
#                     {
#                         "nombre": "Bodys y ropa interior", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Bodys manga corta", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Bodys manga larga", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Bodys de tirantes", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Peleles y ranitas", 
#                         "descripcion": "Prendas de una sola pieza", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Peleles cortos / de verano", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Peleles largos / de invierno", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Ranitas y petos", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Conjuntos", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Conjuntos de algodón", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Conjuntos de punto", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Conjuntos de vestir / ceremonia", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Tops y jerséis", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Camisetas cruzadas", "descripcion": "Fáciles de poner", "genero": "bebé"},
#                             {"nombre": "Camisetas normales", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Blusas y camisas", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Jerséis y chaquetas de punto", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Sudaderas", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Pantalones y braguitas", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Polainas", "descripcion": "Pantalones con pie incluido", "genero": "bebé"},
#                             {"nombre": "Leggings infantiles", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Pantalones suaves", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Vaqueros de bebé", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Cubrepañales y braguitas", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Vestidos y faldas", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Vestidos casuales", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Vestidos de ceremonia", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Faldas", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa de abrigo", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Buzos para nieve / invierno", "descripcion": "Cuerpo entero", "genero": "bebé"},
#                             {"nombre": "Abrigos y chaquetones", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Cazadoras", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Pijamas y sacos de dormir", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Pijamas de cuerpo entero (enterizos)", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Pijamas de dos piezas", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Sacos de dormir", "descripcion": "Para la cuna", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Ropa de baño", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Bañadores pañal", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Bañadores y bikinis", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Camisetas de protección solar UV", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Calzado de bebé", 
#                         "descripcion": "", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Patucos", "descripcion": "Para recién nacidos", "genero": "bebé"},
#                             {"nombre": "Badanas y zapatos sin suela", "descripcion": "Preandantes", "genero": "bebé"},
#                             {"nombre": "Zapatos de primeros pasos", "descripcion": "Con suela flexible", "genero": "bebé"},
#                             {"nombre": "Deportivas de bebé", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Botitas", "descripcion": "", "genero": "bebé"}
#                         ]
#                     },
#                     {
#                         "nombre": "Accesorios de bebé", 
#                         "descripcion": "Complementos esenciales", 
#                         "genero": "bebé",
#                         "hijos": [
#                             {"nombre": "Baberos y bandanas", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Muselinas y gasas", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Arrullos y mantas", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Gorritos y sombreros", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Manoplas antiarañazos", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Calcetines y leotardos", "descripcion": "", "genero": "bebé"},
#                             {"nombre": "Lazos y diademas", "descripcion": "", "genero": "bebé"}
#                         ]
#                     }
#                 ]
#             }
#         ]
#     }
#     # {
#     #     # ==============================================================================
#     #     # 5. CUIDADO Y BELLEZA
#     #     # ==============================================================================
#     #     "nombre": "Cuidado y belleza",
#     #     "descripcion": "",
#     #     "genero": "",
#     #     "hijos": [
#     #         {"nombre": "Maquillaje", "descripcion": "", "genero": ""},
#     #         {"nombre": "Perfume", "descripcion": "", "genero": ""},
#     #         {"nombre": "Cuidado facial", "descripcion": "", "genero": ""},
#     #         {"nombre": "Accesorios de belleza", 
#     #          "descripcion": "", 
#     #          "genero": "",
#     #          "hijos": [
#     #             {"nombre": "Utensilios de peluqueria", "descripcion": "", "genero": ""},
#     #             {"nombre": "Accesorios de cuidado facial", "descripcion": "", "genero": ""},
#     #             {"nombre": "Accesorios de cuidado corporal", "descripcion": "", "genero": ""},
#     #             {"nombre": "Herramients de cuidado de uñas", "descripcion": "", "genero": ""},
#     #             {"nombre": "Accesorios de maquillaje", "descripcion": "", "genero": ""}
#     #             ]
#     #         },
#     #         {"nombre": "Cuidado de las manos", "descripcion": "", "genero": ""},
#     #         {"nombre": "Manicura", "descripcion": "", "genero": ""},
#     #         {"nombre": "Cuidado corporal", "descripcion": "", "genero": ""},
#     #         {"nombre": "Cuidado del cabello", "descripcion": "", "genero": ""},
#     #         {"nombre": "Otros productos de belleza", "descripcion": "", "genero": ""}
#     #     ]
#     # }
# ]

# # ==============================================================================
# # 2. LÓGICA DE SINCRONIZACIÓN (UPSERT) - EVITA ERROR DE LLAVES FORÁNEAS
# # ==============================================================================

# def sincronizar_recursivo(db: Session, nodo: dict, parent_id: int = None):
#     nombre = nodo["nombre"]
    
#     # 1. Omitir si se llama "Todos"
#     if nombre.lower() == "todos":
#         return

#     # 2. Preparar datos de género
#     genero_valor = nodo.get("genero")
#     if genero_valor == "": 
#         genero_valor = None 

#     # 3. Buscar si la categoría ya existe bajo el mismo padre
#     categoria = db.query(Categoria).filter(
#         Categoria.nombre == nombre,
#         Categoria.parent_id == parent_id
#     ).first()

#     if categoria:
#         # Actualizar si ya existe (sin cambiar el ID)
#         categoria.genero = genero_valor
#         categoria.descripcion = nodo.get("descripcion", "")
#         db.flush()
#         print(f"🔄 Sincronizada: {nombre}")
#     else:
#         # Crear si es nueva
#         categoria = Categoria(
#             nombre=nombre,
#             descripcion=nodo.get("descripcion", ""),
#             genero=genero_valor,
#             parent_id=parent_id
#         )
#         db.add(categoria)
#         db.flush()
#         print(f"✨ Creada: {nombre}")

#     # 4. Procesar hijos
#     for hijo in nodo.get("hijos", []):
#         sincronizar_recursivo(db, hijo, parent_id=categoria.id)

# def poblar_categorias():
#     db = SessionLocal()
#     try:
#         print("🚀 Iniciando sincronización de categorías...")
#         # NOTA: Ya no usamos limpiar_tablas() para evitar errores FK y pérdida de IDs
#         for cat in categorias_master:
#             sincronizar_recursivo(db, cat)
            
#         db.commit()
#         print("✅ Categorías actualizadas correctamente sin borrar IDs existentes.")
#     except Exception as e:
#         db.rollback()
#         print(f"❌ Error durante la sincronización: {e}")
#     finally:
#         db.close()

# if __name__ == "__main__":
#     Base.metadata.create_all(bind=engine)
#     poblar_categorias()























































































# # from sqlalchemy.orm import Session
# # from app.db.database import SessionLocal, engine, Base

# # from app.models.categorias_model import Categoria
# # from app.models.producto_model import Producto
# # from app.models.marcas_model import Marca
# # from app.models.variantes_model import Variante
# # from app.models.variante_imagen_model import Imagen
# # from app.models.ventas_model import Venta
# # from app.models.atributo_model import Atributo, ValorAtributo
# # from app.models.stock_model import Stock
# # from app.models.proveedores_model import Proveedor

# # # ==============================================================================
# # # 1. DATOS MAESTROS (Estructura Distribuida por Tipo de Producto)
# # # ==============================================================================

# # categorias_master = [
# #     {
# #         # ==============================================================================
# #         # 1. ROPA
# #         # ==============================================================================
# #         "nombre": "Ropa",
# #         "descripcion": "Ropa general",
# #         "genero": "", 
# #         "hijos": [
# #             # ----- MUJER -----
# #             {
# #                 "nombre": "Faldas", 
# #                 "descripcion": "Minifaldas, midi, largas",
# #                 "genero": "mujer",
# #                 "hijos": [
# #                     {"nombre": "Minifaldas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Faldas por la rodilla", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Faldas midi", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Faldas largas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Faldas asimétricas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Falda-pantalón", "descripcion": "", "genero": "mujer"},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Vestidos",
# #                 "genero": "mujer",
# #                 "hijos": [
# #                     {"nombre": "Vestidos cortos / Mini", "genero": "mujer"},
# #                     {"nombre": "Vestidos midi", "genero": "mujer"},
# #                     {"nombre": "Vestidos largos / Maxi", "genero": "mujer"},
# #                     {"nombre": "Vestidos vaqueros", "genero": "mujer"},
# #                     {"nombre": "Vestidos de punto", "genero": "mujer"},
# #                     {"nombre": "Vestidos camiseros", "genero": "mujer"},
# #                     {"nombre": "Vestidos formales", "genero": "mujer"},
# #                     {"nombre": "Vestidos informales", "genero": "mujer"},
# #                     {"nombre": "Vestidos sin tirantes", "genero": "mujer"},
# #                     {"nombre": "Vestidos negros", "genero": "mujer"},
# #                     {"nombre": "Vestidos de verano / Playeros", "genero": "mujer"},
# #                     {"nombre": "Vestidos de invierno", "genero": "mujer"},
# #                     {
# #                         "nombre": "Ocasiones especiales",
# #                         "genero": "mujer",
# #                         "hijos": [
# #                             {"nombre": "Vestidos de fiesta y cóctel", "genero": "mujer"},
# #                             {"nombre": "Vestidos de novia", "genero": "mujer"},
# #                             {"nombre": "Vestidos de graduación", "genero": "mujer"},
# #                             {"nombre": "Vestidos de noche", "genero": "mujer"},
# #                             {"nombre": "Espalda descubierta", "genero": "mujer"},
# #                         ]
# #                     },
# #                     {"nombre": "Otros vestidos", "genero": "mujer"},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Camisetas y tops",
# #                 "descripcion": "Camisas, blusas, tops",
# #                 "genero": "mujer",
# #                 "hijos": [
# #                     {"nombre": "Camisas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "blusas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "chalecos", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Camisetas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Sin mangas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Túnicas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Crop tops", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Manga corta", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Manga 3/4", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Manga Larga", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Bodies", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Hombros descubiertos", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Cuello alto", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Peplum", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Halter", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Otros tops", "descripcion": "", "genero": "mujer"},
# #                 ]
# #             },
# #             # ----- HOMBRE -----
# #             {
# #                 "nombre": "Camisetas y camisas",
# #                 "descripcion": "",
# #                 "genero": "hombre", 
# #                 "hijos": [
# #                     {
# #                         "nombre": "Camisas", 
# #                         "descripcion": "", 
# #                         "genero": "",
# #                         "hijos":[
# #                             {"nombre": "Camisas de cuadros", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisas vaqueras", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisas lisas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisas estampadas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisas de rayas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Otras camisetas", "descripcion": "", "genero": ""},
# #                         ]
# #                     },
# #                     {
# #                         "nombre": "camisetas", 
# #                         "descripcion": "", 
# #                         "genero": "",
# #                         "hijos":[
# #                             {"nombre": "Camisetas lisas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisetas estampadas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisetas de rayas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisetas de manga larga", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisetas cuello redondo", "descripcion": "", "genero": ""},
# #                             {"nombre": "Camisetas cuello v", "descripcion": "", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Polos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Henley", "descripcion": "", "genero": ""},
# #                     {"nombre": "Camisetas sin mangas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             # ----- COMUNES (Mujer/Hombre) -----
# #             {"nombre": "Falda pantalon", "descripcion": "", "genero": "mujer"},
# #             {
# #                 "nombre": "Vaqueros",
# #                 "descripcion": "Partes de abajo",
# #                 "genero": "", 
# #                 "hijos": [
# #                     {"nombre": "Vaqueros boyfriend", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Vaqueros tobilleros", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Vaqueros de campana", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros de cintura alta", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros rotos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros pitillo", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros rectos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros ajustados", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Otros Vaqueros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Pantalones y leggins",
# #                 "descripcion": "",
# #                 "genero": "mujer", 
# #                 "hijos": [
# #                     {"nombre": "Pantalones tobilleros y chinos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones anchos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones ptitillo", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones de pinzas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones rectos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones de cuero", "descripcion": "", "genero": ""},
# #                     {"nombre": "Leggins", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones harén", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros Pantalones", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Pantalones",
# #                 "descripcion": "",
# #                 "genero": "", 
# #                 "hijos": [
# #                     {"nombre": "Chinos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Joggers", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones pitillos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Capri", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones de pinzas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones anchos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Shorts",
# #                 "descripcion": "",
# #                 "genero": "", 
# #                 "hijos": [
# #                     {"nombre": "De cintura baja", "descripcion": "", "genero": ""},
# #                     {"nombre": "De cintura alta", "descripcion": "", "genero": ""},
# #                     {"nombre": "Hasta la rodilla", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vaqueros", "descripcion": "", "genero": ""},
# #                     {"nombre": "De encaje", "descripcion": "", "genero": ""},
# #                     {"nombre": "De cuero", "descripcion": "", "genero": ""},
# #                     {"nombre": "Estilo cargo", "descripcion": "", "genero": ""},
# #                     {"nombre": "Capri", "descripcion": "", "genero": ""},
# #                     {"nombre": "Chinos", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Estilo cargo", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Otros shorts", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Monos",
# #                 "descripcion": "",
# #                 "genero": "mujer", 
# #                 "hijos": [
# #                     {"nombre": "Monos largos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Monos cortos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros monos", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Abrigos y Chaquetas",
# #                 "descripcion": "Prendas de exterior y abrigo",
# #                 "genero": "", 
# #                 "hijos": [
# #                     {
# #                         "nombre": "Abrigos",
# #                         "genero": "",
# #                         "hijos": [
# #                             {"nombre": "Trencas", "genero": ""},
# #                             {"nombre": "Sobretodos y abrigos largos", "genero": ""},
# #                             {"nombre": "Parkas", "genero": ""},
# #                             {"nombre": "Chaquetones marineros", "genero": ""},
# #                             {"nombre": "Impermeables", "genero": ""},
# #                             {"nombre": "Gabardinas", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Chalecos", "genero": ""},
# #                     {
# #                         "nombre": "Chaquetas",
# #                         "genero": "",
# #                         "hijos": [
# #                             {"nombre": "Cazadoras bikers", "genero": ""},
# #                             {"nombre": "Chaquetas bombers", "genero": ""},
# #                             {"nombre": "Cazadoras vaqueras", "genero": ""},
# #                             {"nombre": "Chaquetas militares y utilitarias", "genero": ""},
# #                             {"nombre": "Forros polares", "genero": ""},
# #                             {"nombre": "Chaquetas harrington", "genero": ""},
# #                             {"nombre": "Chaquetas de plumas", "genero": ""},
# #                             {"nombre": "Chaquetas acolchadas", "genero": ""},
# #                             {"nombre": "Sobrecamisas", "genero": ""},
# #                             {"nombre": "Chaquetas de esquí y snow", "genero": ""},
# #                             {"nombre": "Chaquetas universitarias", "genero": ""},
# #                             {"nombre": "Cortavientos", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Ponchos", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Jerséis y sudaderas",
# #                 "descripcion": "",
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Sudaderas con capucha", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sudaderas sin capucha", "descripcion": "", "genero": ""},
# #                     {
# #                         "nombre": "Jerséis", 
# #                         "descripcion": "Jerséis de punto", 
# #                         "genero": "",
# #                         "hijos": [
# #                             {"nombre": "Cuello alto", "descripcion": "Turtleneck", "genero": ""},
# #                             {"nombre": "Cuello de pico", "descripcion": "Escote en V", "genero": ""},
# #                             {"nombre": "Cuello redondo", "descripcion": "Crew neck", "genero": ""},
# #                             {"nombre": "Jerséis largos", "descripcion": "Tipo túnica o oversize", "genero": "mujer"},
# #                             {"nombre": "Jerséis de punto fino", "descripcion": "", "genero": ""},
# #                             {"nombre": "Jerséis de punto grueso", "descripcion": "", "genero": ""},
# #                             {"nombre": "Manga 3/4", "descripcion": "", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Kimonos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Cárdigan", "descripcion": "", "genero": ""},
# #                     {"nombre": "Boleros", "descripcion": "", "genero": ""},
# #                     {"nombre": "Chalecos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros jerséis y sudaderas", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Trajes y blazers",
# #                 "descripcion": "",
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Blazers", "descripcion": "", "genero": ""},
# #                     {"nombre": "Trajes de pantalón", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones de trajes", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Chalecos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Trajes", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Trajes de boda", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Trajes de falda", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Piezas de traje", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros trajes y blazers", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Ropa Interior",
# #                 "descripcion": "",
# #                 "genero": "hombre", 
# #                 "hijos": [
# #                     {"nombre": "Calzoncillos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Calcetines", "descripcion": "", "genero": ""},
# #                     {"nombre": "Albornoces", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Ropa de baño",
# #                 "descripcion": "Playa y piscina",
# #                 "genero": "mujer",
# #                 "hijos": [
# #                     {"nombre": "Bikinis", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Bañadores", "descripcion": "Una pieza o short", "genero": ""},
# #                     {"nombre": "Trikinis", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Pareos y caftanes", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Otros", "descripcion": "", "genero": "mujer"},
# #                 ]
# #             },
# #             {"nombre": "Bañadores", "descripcion": "", "genero": "mujer"},
# #             {
# #                 "nombre": "Lencería y pijamas",
# #                 "descripcion": "",
# #                 "genero": "mujer", 
# #                 "hijos": [
# #                     {"nombre": "Sujetadores", "descripcion": "", "genero": ""},
# #                     {"nombre": "Braguitas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Conjuntos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Lencería moldeadora", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pijamas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Batas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Medias", "descripcion": "", "genero": ""},
# #                     {"nombre": "Calcetines", "descripcion": "", "genero": ""},
# #                     {"nombre": "Accersorios de lencería", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Pijamas",
# #                 "descripcion": "",
# #                 "genero": "hombre", 
# #                 "hijos": [
# #                     {"nombre": "Pijama de una sola pieza", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones de pijama", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pijamas completos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Camisetas de pijama", "descripcion": "", "genero": ""},
# #                     {"nombre": "otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Premamá",
# #                 "descripcion": "",
# #                 "genero": "mujer", 
# #                 "hijos": [
# #                     {"nombre": "Camisetas y blusas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vestidos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Faldas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones", "descripcion": "", "genero": ""},
# #                     {"nombre": "Shorts", "descripcion": "", "genero": ""},
# #                     {"nombre": "Monos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sudaderas y jerseís", "descripcion": "", "genero": ""},
# #                     {"nombre": "Abrigos y cazadoras", "descripcion": "", "genero": ""},
# #                     {"nombre": "Bañadores y pareos", "descripcion": "", "genero": ""},
# #                     {
# #                         "nombre": "Ropa interior", 
# #                         "descripcion": "", 
# #                         "genero": "",
# #                         "hijos":[
# #                             {"nombre": "Ropa interior", "descripcion": "", "genero": ""},
# #                             {"nombre": "Pijamas", "descripcion": "", "genero": ""},
# #                             {"nombre": "sujetadores premamá y posparto", "descripcion": "", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Ropa de deporte", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Ropa deportiva",
# #                 "descripcion": "",
# #                 "genero": "", 
# #                 "hijos": [
# #                     {"nombre": "Ropa de abrigo", "descripcion": "", "genero": ""},
# #                     {"nombre": "Ropa de entrenamiento", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Chándales", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pantalones", "descripcion": "", "genero": ""},
# #                     {"nombre": "Shorts", "descripcion": "", "genero": ""},
# #                     {"nombre": "Vestidos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Faldas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Tops y camisetas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Camisetas de equipos", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sudaderas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sudaderas y suéteres", "descripcion": "", "genero": "hombre"},
# #                     {
# #                         "nombre": "Accesorios", 
# #                         "descripcion": "", 
# #                         "genero": "",
# #                         "hijos":[
# #                             {"nombre": "Gafas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Guantes", "descripcion": "", "genero": ""},
# #                             {"nombre": "Gorras", "descripcion": "", "genero": ""},
# #                             {"nombre": "Bufandas", "descripcion": "", "genero": ""},
# #                             {"nombre": "Muñequeras", "descripcion": "", "genero": ""},
# #                         ]
# #                     },
# #                     {"nombre": "Sujetadores", "descripcion": "", "genero": ""},
# #                     {"nombre": "Otros", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {"nombre": "Disfraces y trajes especiales", "descripcion": "", "genero": ""},
# #             {"nombre": "Otras prendas", "descripcion": "", "genero": ""},
            
# #             # ----- ROPA INFANTIL (Añadido dentro de Ropa) -----
# #             {
# #                 "nombre": "Ropa Niña",
# #                 "descripcion": "Prendas de vestir para niñas",
# #                 "genero": "niña",
# #                 "hijos": [
# #                     {"nombre": "Camisetas y tops niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Vestidos y faldas niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Pantalones y vaqueros niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Jerséis y sudaderas niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Abrigos y chaquetas niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Ropa de baño niña", "descripcion": "", "genero": "niña"},
# #                     {"nombre": "Ropa interior y pijamas niña", "descripcion": "", "genero": "niña"},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Ropa Niño",
# #                 "descripcion": "Prendas de vestir para niños",
# #                 "genero": "niño",
# #                 "hijos": [
# #                     {"nombre": "Camisetas y camisas niño", "descripcion": "", "genero": "niño"},
# #                     {"nombre": "Pantalones y vaqueros niño", "descripcion": "", "genero": "niño"},
# #                     {"nombre": "Jerséis y sudaderas niño", "descripcion": "", "genero": "niño"},
# #                     {"nombre": "Abrigos y chaquetas niño", "descripcion": "", "genero": "niño"},
# #                     {"nombre": "Ropa de baño niño", "descripcion": "", "genero": "niño"},
# #                     {"nombre": "Ropa interior y pijamas niño", "descripcion": "", "genero": "niño"},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Ropa Bebé",
# #                 "descripcion": "Prendas para bebés (0-36 meses)",
# #                 "genero": "bebé",
# #                 "hijos": [
# #                     {"nombre": "Bodys y ropa interior bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Peleles y ranitas", "descripcion": "Prendas de una sola pieza", "genero": "bebé"},
# #                     {"nombre": "Conjuntos bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Tops y jerséis bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Pantalones y polainas bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Vestidos y faldas bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Ropa de abrigo bebé", "descripcion": "Buzos para nieve / invierno", "genero": "bebé"},
# #                     {"nombre": "Pijamas y sacos de dormir", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Ropa de baño bebé", "descripcion": "", "genero": "bebé"},
# #                 ]
# #             }
# #         ]
# #     },
# #     {
# #         # ==============================================================================
# #         # 2. CALZADO
# #         # ==============================================================================
# #         "nombre": "Calzado",
# #         "descripcion": "Zapatos y zapatillas",
# #         "genero": "",
# #         "hijos": [
# #             {
# #                 "nombre": "Zapatillas", 
# #                 "descripcion": "Sneakers y deportivas", 
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Running", "descripcion": "", "genero": ""},
# #                     {"nombre": "Casual / Lona", "descripcion": "", "genero": ""},
# #                     {"nombre": "Futbol", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Botas y Botines", 
# #                 "descripcion": "", 
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Botas altas", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Botines", "descripcion": "", "genero": ""},
# #                     {"nombre": "Botas de agua", "descripcion": "", "genero": ""},
# #                     {"nombre": "Botas militares", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Zapatos formales", 
# #                 "descripcion": "", 
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Tacones", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Mocasines", "descripcion": "", "genero": ""},
# #                     {"nombre": "Oxford / Derby", "descripcion": "", "genero": "hombre"},
# #                     {"nombre": "Alpargatas", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Sandalias", 
# #                 "descripcion": "", 
# #                 "genero": "",
# #                  "hijos": [
# #                     {"nombre": "Sandalias planas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sandalias de tacón", "descripcion": "", "genero": "mujer"},
# #                     {"nombre": "Chanclas", "descripcion": "", "genero": ""},
# #                  ]
# #             },
# #             # ----- CALZADO INFANTIL (Añadido dentro de Calzado) -----
# #             {"nombre": "Calzado niña", "descripcion": "Zapatillas, botas, sandalias, bailarinas", "genero": "niña"},
# #             {"nombre": "Calzado niño", "descripcion": "Zapatillas, botas, sandalias, zapatos escolares", "genero": "niño"},
# #             {
# #                 "nombre": "Calzado bebé", 
# #                 "descripcion": "Zapatos primeros pasos y patucos", 
# #                 "genero": "bebé",
# #                 "hijos": [
# #                     {"nombre": "Patucos", "descripcion": "Para recién nacidos", "genero": "bebé"},
# #                     {"nombre": "Zapatos primeros pasos", "descripcion": "Con suela flexible", "genero": "bebé"},
# #                     {"nombre": "Deportivas bebé", "descripcion": "", "genero": "bebé"},
# #                 ]
# #             }
# #         ]
# #     },
# #     {
# #         # ==============================================================================
# #         # 3. BOLSOS
# #         # ==============================================================================
# #         "nombre": "Bolsos",
# #         "descripcion": "",
# #         "genero": "",
# #         "hijos":[
# #             {"nombre": "Mochilas", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsas de playa", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Maletines", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsos cubo", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Riñoneras", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsos de fiesta", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Portatrajes", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsa de deporte, Bolso de deporte, bolsa de gimnasio", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsos de mano", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Bolsos boho", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Bolsas de viaje", "descripcion": "", "genero": ""},
# #             {"nombre": "Maletas", "descripcion": "", "genero": ""},
# #             {"nombre": "Neceseres", "descripcion": "", "genero": ""},
# #             {"nombre": "Satchels", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Bolsos de hombro", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Bolsos tote", "descripcion": "", "genero": "mujer"},
# #             {"nombre": "Monederos y carteras", "descripcion": "", "genero": ""},
# #             {"nombre": "Bolsos de pulseras", "descripcion": "", "genero": "mujer"}
# #         ]
# #     },
# #     {
# #         # ==============================================================================
# #         # 4. ACCESORIOS
# #         # ==============================================================================
# #         "nombre": "Accesorios",
# #         "descripcion": "",
# #         "genero": "",
# #         "hijos": [
# #             {"nombre": "Bandanas y pañuelos para el pelo", "descripcion": "", "genero": ""},
# #             {"nombre": "Cinturones", "descripcion": "", "genero": ""},
# #             {"nombre": "Guantes", "descripcion": "", "genero": ""},
# #             {"nombre": "Accesorios de cabello", "descripcion": "", "genero": ""},
# #             {"nombre": "Pañuelos", "descripcion": "", "genero": ""},
# #             {
# #                 "nombre": "Sombreros y gorros", 
# #                 "descripcion": "", 
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Pasamontañas", "descripcion": "", "genero": ""},
# #                     {"nombre": "Gorros de lana", "descripcion": "", "genero": ""},
# #                     {"nombre": "Gorros", "descripcion": "", "genero": ""},
# #                     {"nombre": "Orejeras", "descripcion": "", "genero": ""},
# #                     {"nombre": "Tocados", "descripcion": "", "genero": ""},
# #                     {"nombre": "Sombreros", "descripcion": "", "genero": ""},
# #                     {"nombre": "Diademas y cintas", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {
# #                 "nombre": "Joyeria", 
# #                 "descripcion": "", 
# #                 "genero": "",
# #                 "hijos": [
# #                     {"nombre": "Tobilleras", "descripcion": "", "genero": ""},
# #                     {"nombre": "Joyas corporales", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pulsares", "descripcion": "", "genero": ""},
# #                     {"nombre": "Broches", "descripcion": "", "genero": ""},
# #                     {"nombre": "Colgantes y dijes", "descripcion": "", "genero": ""},
# #                     {"nombre": "Pendientes", "descripcion": "", "genero": ""},
# #                     {"nombre": "Conjuntos de joyería", "descripcion": "", "genero": ""},
# #                     {"nombre": "Collares", "descripcion": "", "genero": ""},
# #                     {"nombre": "Anillos", "descripcion": "", "genero": ""},
# #                 ]
# #             },
# #             {"nombre": "Llaveros", "descripcion": "", "genero": ""},
# #             {"nombre": "Bufandas y pañuelos", "descripcion": "", "genero": ""},
# #             {"nombre": "Gafas de sol", "descripcion": "", "genero": ""},
# #             {"nombre": "Paraguas", "descripcion": "", "genero": ""},
# #             {"nombre": "Relojes", "descripcion": "", "genero": ""},
            
# #             # ----- ACCESORIOS INFANTILES (Añadidos dentro de Accesorios) -----
# #             {"nombre": "Accesorios niña", "descripcion": "Diademas, lazos, bufandas, mochilas", "genero": "niña"},
# #             {"nombre": "Accesorios niño", "descripcion": "Gorras, cinturones, bufandas, mochilas", "genero": "niño"},
# #             {
# #                 "nombre": "Accesorios de bebé", 
# #                 "descripcion": "Complementos esenciales", 
# #                 "genero": "bebé",
# #                 "hijos": [
# #                     {"nombre": "Baberos y bandanas", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Muselinas y gasas", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Arrullos y mantas", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Gorritos y sombreros de bebé", "descripcion": "", "genero": "bebé"},
# #                     {"nombre": "Manoplas antiarañazos", "descripcion": "", "genero": "bebé"},
# #                 ]
# #             }
# #         ]
# #     }
# # ]

# # # ==============================================================================
# # # 2. LÓGICA DE SINCRONIZACIÓN (UPSERT)
# # # ==============================================================================

# # def sincronizar_recursivo(db: Session, nodo: dict, parent_id: int = None):
# #     nombre = nodo["nombre"]
    
# #     if nombre.lower() == "todos":
# #         return

# #     genero_valor = nodo.get("genero")
# #     if genero_valor == "": 
# #         genero_valor = None 

# #     categoria = db.query(Categoria).filter(
# #         Categoria.nombre == nombre,
# #         Categoria.parent_id == parent_id
# #     ).first()

# #     if categoria:
# #         categoria.genero = genero_valor
# #         categoria.descripcion = nodo.get("descripcion", "")
# #         db.flush()
# #         print(f"🔄 Sincronizada: {nombre}")
# #     else:
# #         categoria = Categoria(
# #             nombre=nombre,
# #             descripcion=nodo.get("descripcion", ""),
# #             genero=genero_valor,
# #             parent_id=parent_id
# #         )
# #         db.add(categoria)
# #         db.flush()
# #         print(f"✨ Creada: {nombre}")

# #     for hijo in nodo.get("hijos", []):
# #         sincronizar_recursivo(db, hijo, parent_id=categoria.id)

# # def poblar_categorias():
# #     db = SessionLocal()
# #     try:
# #         print("🚀 Iniciando sincronización de categorías...")
# #         for cat in categorias_master:
# #             sincronizar_recursivo(db, cat)
            
# #         db.commit()
# #         print("✅ Categorías actualizadas correctamente.")
# #     except Exception as e:
# #         db.rollback()
# #         print(f"❌ Error durante la sincronización: {e}")
# #     finally:
# #         db.close()

# # if __name__ == "__main__":
# #     Base.metadata.create_all(bind=engine)
# #     poblar_categorias()