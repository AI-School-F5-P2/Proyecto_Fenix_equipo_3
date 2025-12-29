from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine, Base

# Importar modelos
from app.models.categorias_model import Categoria
from app.models.producto_model import Producto


def borrar_todas_categorias_seguro(db: Session):
    """
    Borra todas las categorías de forma segura empezando por las hojas
    para evitar violaciones de clave foránea.
    """
    while True:
        hojas = db.query(Categoria).filter(
            ~Categoria.id.in_(
                db.query(Categoria.parent_id).filter(Categoria.parent_id != None)
            )
        ).all()
        if not hojas:
            break
        for hoja in hojas:
            db.delete(hoja)
        db.commit()

def poblar_categorias():
    db: Session = SessionLocal()

    # Borrar todas las categorías de manera segura
    borrar_todas_categorias_seguro(db)

    # ---------------- CATEGORÍAS DEFINIDAS DE FORMA JERÁRQUICA ----------------
    categorias_hierarchy = [
        # ---------------- MUJER ----------------
        {
            "nombre": "Mujer",
            "descripcion": "Moda femenina",
            "hijos": [
                {
                    "nombre": "Ropa",
                    "descripcion": "Prendas de vestir para mujer",
                    "hijos": [
                        {"nombre": "Todos", "descripcion": "Todas las prendas de ropa mujer"},
                        {
                            "nombre": "Abrigos y cazadoras",
                            "descripcion": "Abrigos, chaquetas, ponchos, chalecos",
                            "hijos": [
                                {"nombre": "Todos", "descripcion": "Todos los abrigos y cazadoras"},
                                {"nombre": "Capas y ponchos", "descripcion": "Abrigos amplios y abiertos"},
                                {"nombre": "Abrigos", "descripcion": "Abrigos de diferentes estilos",
                                 "hijos": [
                                     {"nombre": "Trencas", "descripcion": "Abrigo clásico con botones de madera"},
                                     {"nombre": "Abrigos de piel sintética", "descripcion": "Abrigos suaves y cálidos"},
                                     {"nombre": "Sobretodos y abrigos largos", "descripcion": "Abrigos elegantes y largos"},
                                     {"nombre": "Parkas", "descripcion": "Abrigos casuales con capucha"},
                                     {"nombre": "Chaquetones marineros", "descripcion": "Abrigos de botones dobles"},
                                     {"nombre": "Impermeables", "descripcion": "Abrigos resistentes al agua"},
                                     {"nombre": "Gabardinas", "descripcion": "Abrigos largos ligeros"},
                                 ]},
                                {"nombre": "Chalecos", "descripcion": "Prendas sin mangas"},
                                {"nombre": "Chaquetas", "descripcion": "Chaquetas de todo tipo",
                                 "hijos": [
                                     {"nombre": "Todos", "descripcion": "Todos los tipos de chaquetas"},
                                     {"nombre": "Cazadoras biker", "descripcion": "Chaquetas de cuero estilo motociclista"},
                                     {"nombre": "Chaquetas bomber", "descripcion": "Chaquetas cortas con goma"},
                                     {"nombre": "Cazadoras vaqueras", "descripcion": "Chaquetas denim"},
                                     {"nombre": "Chaquetas militares y utilitarias", "descripcion": "Estilo uniforme o con bolsillos"},
                                     {"nombre": "Forros polares", "descripcion": "Chaquetas térmicas de forro polar"},
                                     {"nombre": "Chaquetas de plumas", "descripcion": "Abrigos acolchados ligeros"},
                                     {"nombre": "Chaquetas acolchadas", "descripcion": "Chaquetas con relleno"},
                                     {"nombre": "Sobrecamisas", "descripcion": "Camisas gruesas a modo de chaqueta"},
                                     {"nombre": "Chaquetas de esquí y snow", "descripcion": "Chaquetas técnicas para deporte"},
                                     {"nombre": "Chaquetas universitarias", "descripcion": "Estilo varsity"},
                                     {"nombre": "Cortavientos", "descripcion": "Chaquetas ligeras contra el viento"},
                                 ]}
                            ]
                        },
                        {"nombre": "Jerseys y sudaderas", "descripcion": "Sudaderas, jerseys, cardigans",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": "Todos los tipos de Sudaderas, jerseys, cardigans"},
                             {"nombre": "Sudaderas", "descripcion": ""},
                             {"nombre": "Jerseis", "descripcion": "",
                              "hijos":[
                                  {"nombre": "Todos", "descripcion": ""},
                                  {"nombre": "Cuello de pico", "descripcion": ""},
                                  {"nombre": "cuallo alto", "descripcion": ""},
                                  {"nombre": "Largos", "descripcion": ""},
                                  {"nombre": "De punto", "descripcion": ""},
                                  {"nombre": "Manga 3/4", "descripcion": ""},
                                  {"nombre": "Otros jerséis", "descripcion": ""},
                              ]},
                             {"nombre": "Kimonos", "descripcion": ""},
                             {"nombre": "Cárdigan", "descripcion": ""},
                             {"nombre": "Boleros", "descripcion": ""},
                             {"nombre": "Chalecos", "descripcion": ""},
                             {"nombre": "Otros jerséis y sudaderas", "descripcion": ""},
                         ]},
                        {"nombre": "Trajes y blazers", "descripcion": "Blazers, trajes completos",
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "Blazers", "descripcion": ""},
                            {"nombre": "Trajes de pantalon", "descripcion": ""},
                            {"nombre": "Trajes de falda", "descripcion": ""},
                            {"nombre": "Piezas de traje", "descripcion": ""},
                            {"nombre": "Manga 3/4", "descripcion": ""},
                            {"nombre": "Otros trajes y blazers", "descripcion": ""},
                            ]},
                        {"nombre": "Vestidos", "descripcion": "Todo tipo de vestidos",
                         "hijos":[
                             {"nombre": "Mini", "descripcion": ""},
                             {"nombre": "Midi", "descripcion": ""},
                             {"nombre": "Vestidos Largos", "descripcion": ""},
                             {"nombre": "Ocaciones especiales", "descripcion": "",
                              "Hijos":[
                                  {"nombre": "Todos", "descripcion": ""},
                                  {"nombre": "Fiesta y cóctel", "descripcion": ""},
                                  {"nombre": "Vestidos de novia", "descripcion": ""},
                                  {"nombre": "Graduación", "descripcion": ""},
                                  {"nombre": "Vestidos de noche", "descripcion": ""},
                                  {"nombre": "Espalda descubierta", "descripcion": ""},
                              ]},
                             {"nombre": "Vestidos de verano", "descripcion": ""},
                             {"nombre": "Vestidos de invierno", "descripcion": ""},
                             {"nombre": "Vestidos formales", "descripcion": ""},
                             {"nombre": "Vestidos informales", "descripcion": ""},
                             {"nombre": "vestidos sin tirantes", "descripcion": ""},
                             {"nombre": "Vestidos negros", "descripcion": ""},
                             {"nombre": "Vestidos vaqueros", "descripcion": ""},
                             {"nombre": "Otros Vestidos", "descripcion": ""},
                             
                         ]},
                        {"nombre": "Faldas", "descripcion": "Minifaldas, midi, largas",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Minifaldas", "descripcion": ""},
                             {"nombre": "Faldas por la rodilla", "descripcion": ""},
                             {"nombre": "Faldas midi", "descripcion": ""},
                             {"nombre": "Faldas largas", "descripcion": ""},
                             {"nombre": "Faldas asimétricas", "descripcion": ""},
                             {"nombre": "Fals-pantalón", "descripcion": ""},
                         ]},
                        {
                            "nombre": "Camisetas y tops",
                            "descripcion": "Camisas, blusas, tops",
                            "hijos": [
                                {"nombre": "Camisetas", "descripcion": "Camisetas básicas"},
                                {"nombre": "Blusas", "descripcion": "Blusas de mujer"},
                                {"nombre": "Chalecos", "descripcion": "Chalecos de mujer"},
                                {"nombre": "Sin mangas", "descripcion": "Prendas sin mangas"},
                                {"nombre": "Mangas 3/4", "descripcion": "Prendas con manga 3/4"},
                                {"nombre": "Túnicas", "descripcion": "Túnicas y vestidos sueltos"},
                                {"nombre": "Crop tops", "descripcion": "Camisetas cortas"},
                                {"nombre": "Manga larga", "descripcion": "Camisetas y tops manga larga"},
                                {"nombre": "Bodies", "descripcion": "Bodies de mujer"},
                                {"nombre": "Hombros descubiertos", "descripcion": "Prendas con hombros al descubierto"},
                                {"nombre": "Cuello alto", "descripcion": "Camisetas y tops con cuello alto"},
                                {"nombre": "Peplum", "descripcion": "Prendas peplum"},
                                {"nombre": "Halter", "descripcion": "Prendas tipo halter"},
                                {"nombre": "Otros", "descripcion": "Otros tipos de camisetas y tops"},
                            ]
                        },
                        {"nombre": "Vaqueros", "descripcion": "Diferentes tipos de jeans",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Vaqueros boyfriend", "descripcion": ""},
                             {"nombre": "Vaqueros tobilleros", "descripcion": ""},
                             {"nombre": "Vaqueros de campana", "descripcion": ""},
                             {"nombre": "Vaqueros de cintura alta", "descripcion": ""},
                             {"nombre": "Vaqueros rotos", "descripcion": ""},
                             {"nombre": "Vaqueros pitillo", "descripcion": ""},
                             {"nombre": "Vaqueros rectos", "descripcion": ""},
                             {"nombre": "Otros vaqueros", "descripcion": ""},
                         ]},
                        {"nombre": "Pantalones y leggings", "descripcion": "Pantalones, leggins, joggers",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Pantalones tobilleros y chinos", "descripcion": ""},
                             {"nombre": "Pantalones anchos", "descripcion": ""},
                             {"nombre": "Pantalones pitillos", "descripcion": ""},
                             {"nombre": "Pantalones de pinza", "descripcion": ""},
                             {"nombre": "Pantalones rectos", "descripcion": ""},
                             {"nombre": "Pantalones de cuero", "descripcion": ""},
                             {"nombre": "Leggings", "descripcion": ""},
                             {"nombre": "Pantalones harén", "descripcion": ""},
                             {"nombre": "Otros pantalones", "descripcion": ""},
                         ]},
                        {"nombre": "Shorts", "descripcion": "Prendas cortas",
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "De cintura baja", "descripcion": ""},
                            {"nombre": "De cintura alta", "descripcion": ""},
                            {"nombre": "Hasta la rodilla", "descripcion": ""},
                            {"nombre": "Vaqueros", "descripcion": ""},
                            {"nombre": "De encaje", "descripcion": ""},
                            {"nombre": "De cuero", "descripcion": ""},
                            {"nombre": "Estilo cargo", "descripcion": ""},
                            {"nombre": "Capri", "descripcion": ""},
                            {"nombre": "Otros Shorts", "descripcion": ""},
                         ]},
                        {"nombre": "Monos", "descripcion": "Monos largos o cortos",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Monos largos", "descripcion": ""},
                             {"nombre": "Monos cortos", "descripcion": ""},
                             {"nombre": "Otros monos", "descripcion": ""},
                         ]},
                        {"nombre": "Ropa de baño", "descripcion": "Bañadores, bikinis, pareos",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Bañadores", "descripcion": ""},
                             {"nombre": "Bikinis", "descripcion": ""},
                             {"nombre": "Pareos y caftanes", "descripcion": ""},
                             {"nombre": "Otros", "descripcion": ""},
                         ]},
                        {"nombre": "Lencería y pijamas", "descripcion": "Sujetadores, pijamas, batas",
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Sujetadores", "descripcion": ""},
                             {"nombre": "Braguitas", "descripcion": ""},
                             {"nombre": "Conjuntos", "descripcion": ""},
                             {"nombre": "Lenceria moldeadora", "descripcion": ""},
                             {"nombre": "Pijamas", "descripcion": ""},
                             {"nombre": "Batas", "descripcion": ""},
                             {"nombre": "Medias", "descripcion": ""},
                             {"nombre": "Calcetines", "descripcion": ""},
                             {"nombre": "Accesorios de lencería", "descripcion": ""},
                             {"nombre": "Otros", "descripcion": ""},
                         ]},
                        {"nombre": "Premamá", "descripcion": "Ropa para embarazo",
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "Camisetas y blusas", "descripcion": ""},
                            {"nombre": "Vestidos", "descripcion": ""},
                            {"nombre": "Faldas", "descripcion": ""},
                            {"nombre": "Pantalones", "descripcion": ""},
                            {"nombre": "Shorts", "descripcion": ""},
                            {"nombre": "Monos", "descripcion": ""},
                            {"nombre": "Sudaderas y jerséis", "descripcion": ""},
                            {"nombre": "Abrigos y cazadoras", "descripcion": ""},
                            {"nombre": "Bañadores y pareos", "descripcion": ""},
                            {"nombre": "Ropa interior", "descripcion": "", 
                             "hijos":[
                                {"nombre": "Todos", "descripcion": ""},
                                {"nombre": "Ropa interior", "descripcion": ""},
                                {"nombre": "Pijamas", "descripcion": ""},
                                {"nombre": "Sujetadores premama y posparto", "descripcion": ""},
                             ]},
                            {"nombre": "Ropa de deporte", "descripcion": ""},
                         ]},
                        {"nombre": "Ropa deportiva", "descripcion": "Prendas deportivas",
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "Ropa de abrigo", "descripcion": ""},
                            {"nombre": "Chándales", "descripcion": ""},
                            {"nombre": "Pantalones", "descripcion": ""},
                            {"nombre": "Shorts", "descripcion": ""},
                            {"nombre": "Vestidos", "descripcion": ""},
                            {"nombre": "Faldas", "descripcion": ""},
                            {"nombre": "Tops y camisetas", "descripcion": ""},
                            {"nombre": "Camisetas de equipos", "descripcion": ""},
                            {"nombre": "Sudaderas", "descripcion": ""},
                            {"nombre": "Accesorios", "descripcion": "",
                             "hijos":[
                                {"nombre": "Todos", "descripcion": ""},
                                {"nombre": "Gafas", "descripcion": ""},
                                {"nombre": "Guantes", "descripcion": ""},
                                {"nombre": "Gorras", "descripcion": ""},
                                {"nombre": "Bufandas", "descripcion": ""},
                                {"nombre": "Muñequeras", "descripcion": ""},
                             ]},
                            {"nombre": "Sujetadores", "descripcion": ""},
                            {"nombre": "Otros", "descripcion": ""},
                         ]},
                        {"nombre": "Disfraces y trajes especiales", "descripcion": "Carnaval, cosplay, etc."},
                        {"nombre": "Otras prendas", "descripcion": "Prendas no clasificadas"},
                    ]
                },
                {"nombre": "Calzado", "descripcion": "Zapatos, sandalias, botas, deportivos, etc."},
                {"nombre": "Accesorios", "descripcion": "Bolsos, joyas, bufandas, etc."},
            ]
        },

        # ---------------- HOMBRE ----------------
        {
            "nombre": "Hombre",
            "descripcion": "Moda masculina",
            "hijos": [
                {
                    "nombre": "Ropa",
                    "descripcion": "Prendas de vestir para hombre",
                    "hijos": [
                        {"nombre": "Todos", "descripcion": "Todas las prendas de ropa hombre"},
                        {"nombre": "Vaqueros", "descripcion": "", 
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "Vaqueros rotos", "descripcion": ""},
                            {"nombre": "Vaqueros pitillo", "descripcion": ""},
                            {"nombre": "Vaqueros ajustados", "descripcion": ""},
                            {"nombre": "Vaqueros rectos", "descripcion": ""},
                         ]},
                        {"nombre": "Abrigos y chaquetas", "descripcion": "", 
                         "hijos":[
                            {"nombre": "Todos", "descripcion": ""},
                            {"nombre": "Abrigos", "descripcion": "", 
                             "hijos":[
                                {"nombre": "Todos", "descripcion": ""},
                                {"nombre": "Trencas", "descripcion": ""},
                                {"nombre": "Sobretodos y abrigos largos", "descripcion": ""},
                                {"nombre": "Parkas", "descripcion": ""},
                                {"nombre": "Chaquetones marineros", "descripcion": ""},
                                {"nombre": "Impermeables", "descripcion": ""},
                                {"nombre": "Gabardinas", "descripcion": ""},
                             ]},
                            {"nombre": "Chalecos", "descripcion": ""},
                            {"nombre": "Chaquetas", "descripcion": "", 
                             "hijos":[
                                {"nombre": "Todos", "descripcion": ""},
                                {"nombre": "Cazadoras biker", "descripcion": ""},
                                {"nombre": "Chaquetas bomber", "descripcion": ""},
                                {"nombre": "Cazadoras vaqueras", "descripcion": ""},
                                {"nombre": "Chaquetad militares y utilitarias", "descripcion": ""},
                                {"nombre": "Forros polares", "descripcion": ""},
                                {"nombre": "Chaquetas Harrington", "descripcion": ""},
                                {"nombre": "Chaquetas de plumas", "descripcion": ""},
                                {"nombre": "Chaquetas acolchadas", "descripcion": ""},
                                {"nombre": "Sobrecamisas", "descripcion": ""},
                                {"nombre": "Chaquetas de esqui y snow", "descripcion": ""},
                                {"nombre": "Chaquetas universitarias", "descripcion": ""},
                                {"nombre": "Cortavientos", "descripcion": ""},
                             ]},
                            {"nombre": "Ponchos", "descripcion": ""},
                         ]},
                        {"nombre": "Camisetas y camisas", "descripcion": "", 
                         "hijos":[
                             {"nombre": "Todos", "descripcion": ""},
                             {"nombre": "Camisas", "descripcion": "" , 
                              "hijos":[
                                    {"nombre": "Todos", "descripcion": ""},
                                    {"nombre": "Camisas de cuadros", "descripcion": ""},
                                    {"nombre": "Camisas vaqueras", "descripcion": ""},
                                    {"nombre": "camisas lisas", "descripcion": ""},
                                    {"nombre": "", "descripcion": ""},
                                    {"nombre": "", "descripcion": ""},
                                    {"nombre": "", "descripcion": ""},
                                ]},
                             {"nombre": "Camisetas", "descripcion": ""},
                             {"nombre": "Camisetas sin mangas", "descripcion": ""},
                         ]},
                        {"nombre": "Trajes y blazers", "descripcion": ""},
                        {"nombre": "Jerseís y sudaderas", "descripcion": ""},
                        {"nombre": "Pantalones", "descripcion": ""},
                        {"nombre": "Shorts", "descripcion": ""},
                        {"nombre": "Ropa interior", "descripcion": ""},
                        {"nombre": "Pijamas", "descripcion": ""},
                        {"nombre": "Bañadores", "descripcion": ""},
                        {"nombre": "Ropa y accesorios deportivos", "descripcion": ""},
                        {"nombre": "Disfrases y trajes especiales", "descripcion": ""},
                        {"nombre": "Otras prendas", "descripcion": ""},
                    ]
                },
                {"nombre": "Calzado", "descripcion": "Zapatos, sandalias, botas, deportivos, etc."},
                {"nombre": "Accesorios", "descripcion": "Gafas, relojes, bufandas, etc."},
            ]
        }
    ]

    # ---------------- FUNCION RECURSIVA PARA INSERTAR ----------------
    def insertar_categoria(cat_dict, parent_id=None):
        cat = Categoria(nombre=cat_dict["nombre"], descripcion=cat_dict.get("descripcion"), parent_id=parent_id)
        db.add(cat)
        db.flush()  # Asigna ID automáticamente
        cat_id = cat.id

        for hijo in cat_dict.get("hijos", []):
            insertar_categoria(hijo, parent_id=cat_id)

    # ---------------- INSERTAR TODAS LAS CATEGORÍAS ----------------
    for categoria in categorias_hierarchy:
        insertar_categoria(categoria)

    db.commit()
    db.close()
    print("✅ Categorías insertadas correctamente y escalables.")

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    poblar_categorias()











