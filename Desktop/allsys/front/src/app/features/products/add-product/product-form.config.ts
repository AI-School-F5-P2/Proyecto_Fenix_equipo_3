// app/pages/products/add-product/product-form.config.ts


export type EstadoPrenda = 'nuevo' | 'segunda_mano';

export interface Categoria {
  id: number;
  nombre: string;
  parent_id: number | null;
  // Añade aquí otros campos si tu backend los envía (ej: slug, imagen...)
}

export interface AtributoBackend { id?: number; nombre: string; valor: any; }

export interface StockBackend {
  propietario_id: any; donar_ganancias?: boolean;
  id: number; sku: string; cantidad: number; precio_compra: number;
  precio_venta: number; fecha_compra: string; proveedor_id?: number | null;
  proveedor?: { id: number; nombre_proveedor: string };
  etiqueta?: string | null; descuento?: number; publicar_web: boolean;
  publicar_vinted: boolean; publicar_wallapop: boolean; atributos: AtributoBackend[];
  orden?: number; ubicacion: string;
}

export interface VarianteBackend {
  id: number; sku: string; identidad_variante: string; hex_identidad: string;
  descripcion: string; imagenes: string[]; stocks: StockBackend[];
  orden?: number;
}

export interface ProductoBackend {
  id: number; nombre: string; descripcion: string; tipo: string;
  estado: EstadoPrenda; publico_objetivo: string; categoria_id: number;
  marca_id: number; variantes: VarianteBackend[]; marca?: Marca; es_vintage?: boolean; epoca?: string | null;
}

export interface StockVariante {
  id?: number; sku: string; atributos: any[]; stock: number; talla?: string | null | any;
  precio_compra: number; precio_venta: number; descuento: number; donar_ganancias?: boolean;
  proveedor: string; proveedor_id?: number | null; fecha_compra: string;
  publicar_vinted: boolean; publicar_wallapop: boolean; publicar_web: boolean;
  etiqueta?: string; ubicacion: string; temp_id?: string; id_manual?: number | null; propietario_id?: number | null;
}

export interface Marca { id?: number; nombre: string; isNew?: boolean; }

export interface Variante {
  id?: number; temp_id: string; identidad_variante: string; hex_identidad: string;
  stocks: StockVariante[]; imagenes: string[]; imagenesFiles: (File | null)[];
  descripcion: string;
}

// --- CONSTANTES ---

// export interface Color {
//   hex: string;
//   nombre: string;
//   claro?: boolean;
// }

export interface Color {
  hex: string;
  nombre: string;
  claro?: boolean;
}

export const COLORES_PALETA = [
  // Neutros y Escala de Grises
  { hex: '#000000', nombre: 'Negro' },
  { hex: '#4B4B4B', nombre: 'Gris Oscuro' },
  { hex: '#BEBEBE', nombre: 'Gris Claro' },
  { hex: '#FFFFFF', nombre: 'Blanco' },
  { hex: '#F5F5DC', nombre: 'Beige' },
  { hex: '#D2B48C', nombre: 'Arena / Tan' },
  { hex: '#8B4513', nombre: 'Marrón Chocolate' },
  { hex: '#C19A6B', nombre: 'Camel' },

  // Rojos y Rosas
  { hex: '#FF0000', nombre: 'Rojo' },
  { hex: '#800000', nombre: 'Burdeos' },
  { hex: '#FFC0CB', nombre: 'Rosa Pastel' },
  { hex: '#FF69B4', nombre: 'Fucsia' },
  { hex: '#FF7F50', nombre: 'Coral' },

  // Azules
  { hex: '#000080', nombre: 'Azul Marino' },
  { hex: '#1560BD', nombre: 'Azul Denim' },
  { hex: '#007FFF', nombre: 'Azul Royal' },
  { hex: '#ADD8E6', nombre: 'Azul Celeste' },

  // Verdes y Amarillos
  { hex: '#556B2F', nombre: 'Verde Oliva' },
  { hex: '#008000', nombre: 'Verde' },
  { hex: '#E1AD01', nombre: 'Mostaza' },
  { hex: '#FFFF00', nombre: 'Amarillo' },
  { hex: '#FFA500', nombre: 'Naranja' },

  // Metales Específicos (Clave para Joyería)
  { hex: '#FFD700', nombre: 'Dorado' },
  { hex: '#C0C0C0', nombre: 'Plateado' },
  { hex: '#B76E79', nombre: 'Oro Rosa' }, // Tono rosado metálico
  { hex: '#B87333', nombre: 'Cobre' },    // Tono rojizo/naranja metálico
  { hex: '#CD7F32', nombre: 'Bronce' },   // Tono café metálico
  { hex: '#E5E4E2', nombre: 'Platino / Acero' }
];

export const TALLAS_ROPA = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '32', '34', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56', 'Única'];
export const MATERIALES_ROPA = ['Algodón', 'Poliéster', 'Lino', 'Lana / Cachemira', 'Seda', 'Cuero / Piel', 'Denim / Vaquero', 'Otro'];
export const TALLAS_CALZADO = ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45'];
export const MATERIALES_JOYERIA = ['Oro Amarillo 18K', 'Oro Blanco 18K', 'Oro Rosa 18K', 'Plata de Ley (925)', 'Acero Inoxidable', 'Latón Bañado', 'Cuero'];
export const PIEDRAS_JOYERIA = ['Sin piedra', 'Circonita Cúbica', 'Cristal', 'Diamante', 'Esmeralda', 'Rubí', 'Zafiro', 'Perla', 'Otra'];
export const COLORES_PIEDRA = ['Blanco / Transparente', 'Azul', 'Verde', 'Rojo', 'Rosa', 'Multicolor', 'Negro'];

export const ATRIBUTOS_BASE = [{ nombre: 'peso_kg', tipo: 'number' }];

export const ATRIBUTOS_POR_TIPO: Record<string, any[]> = {
    ropa_superior: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'talla', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'sisa_a_sisa_cm', tipo: 'number' }, { nombre: 'hombros_cm', tipo: 'number' }, { nombre: 'largo_total_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    ropa_inferior: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'talla', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'cintura_cm', tipo: 'number' }, { nombre: 'cadera_cm', tipo: 'number' }, { nombre: 'largo_pierna_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    calzado: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'numero', tipo: 'select', opciones: TALLAS_CALZADO }, { nombre: 'longitud_plantilla_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: ['Cuero', 'Sintético', 'Lona', 'Goma'] }],
    bolsos: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'ancho_cm', tipo: 'number' }, { nombre: 'alto_cm', tipo: 'number' }, { nombre: 'profundidad_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: ['Cuero', 'Lona', 'Sintético'] }],
    joyeria_anillos: [{ nombre: 'talla_anillo', tipo: 'text' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_JOYERIA }, { nombre: 'piedra', tipo: 'select', opciones: PIEDRAS_JOYERIA }, { nombre: 'color_piedra', tipo: 'select', opciones: COLORES_PIEDRA }],
    joyeria_general: [{ nombre: 'material', tipo: 'select', opciones: MATERIALES_JOYERIA }, { nombre: 'piedra', tipo: 'select', opciones: PIEDRAS_JOYERIA }, { nombre: 'color_piedra', tipo: 'select', opciones: COLORES_PIEDRA }],
    perfumeria: [{ nombre: 'capacidad_ml', tipo: 'number' }, { nombre: 'concentracion', tipo: 'select', opciones: ['EDT', 'EDP', 'Parfum'] }],
    accesorios: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }, { nombre: 'dimensiones_notas', tipo: 'text' }],
    guantes: [{ nombre: 'color', tipo: 'color-dropdown' }, { nombre: 'talla_guantes', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    belleza: [{ nombre: 'cantidad_ml_g', tipo: 'number' }, { nombre: 'formato', tipo: 'text' }]
};

// export const MAPEO_IDENTIDAD_POR_TIPO: Record<string, string> = {
//     joyeria_anillos: 'material',
//     joyeria_collares: 'material',
//     joyeria_general: 'material',
//     perfumeria: 'capacidad_ml',
//     belleza: 'cantidad_ml_g'
// };