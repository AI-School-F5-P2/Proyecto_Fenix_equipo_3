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
  id: number; sku: string; cantidad: number; precio_compra: number;
  precio_venta: number; fecha_compra: string; proveedor_id?: number | null;
  proveedor?: { id: number; nombre_proveedor: string };
  etiqueta?: string | null; descuento?: number; publicar_web: boolean;
  publicar_vinted: boolean; publicar_wallapop: boolean; atributos: AtributoBackend[];
  orden?: number;
}

export interface VarianteBackend {
  id: number; sku: string; identidad_variante: string; hex_identidad: string;
  ubicacion: string; descripcion: string; imagenes: string[]; stocks: StockBackend[];
  orden?: number;
}

export interface ProductoBackend {
  id: number; nombre: string; descripcion: string; tipo: string;
  estado: EstadoPrenda; publico_objetivo: string; categoria_id: number;
  marca_id: number; variantes: VarianteBackend[]; marca?: Marca;
}

export interface StockVariante {
  id?: number; sku: string; atributos: any[]; stock: number;
  precio_compra: number; precio_venta: number; descuento: number;
  proveedor: string; proveedor_id?: number | null; fecha_compra: string;
  publicar_vinted: boolean; publicar_wallapop: boolean; publicar_web: boolean;
  etiqueta?: string;
}

export interface Marca { id?: number; nombre: string; isNew?: boolean; }

export interface Variante {
  id?: number; temp_id: string; identidad_variante: string; hex_identidad: string;
  stocks: StockVariante[]; imagenes: string[]; imagenesFiles: (File | null)[];
  ubicacion: string; descripcion: string;
}

// --- CONSTANTES ---
export const ATRIBUTOS_BASE = [{ nombre: 'peso_kg', tipo: 'number' }, { nombre: 'color', tipo: 'color-dropdown' }];

export const COLORES_PALETA = [
    { hex: '#000000', nombre: 'Negro' }, { hex: '#FFFFFF', nombre: 'Blanco' },
    { hex: '#4B4B4B', nombre: 'Gris Oscuro' }, { hex: '#BEBEBE', nombre: 'Gris Claro' },
    { hex: '#F5F5DC', nombre: 'Beige' }, { hex: '#000080', nombre: 'Azul Marino' },
    { hex: '#1560BD', nombre: 'Azul Denim' }, { hex: '#FF0000', nombre: 'Rojo' },
    { hex: '#800000', nombre: 'Burdeos' }, { hex: '#FFD700', nombre: 'Dorado' },
    { hex: '#C0C0C0', nombre: 'Plateado' }
];

export const TALLAS_ROPA = ['XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL', '32', '34', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56', 'Única'];
export const MATERIALES_ROPA = ['Algodón', 'Poliéster', 'Lino', 'Lana / Cachemira', 'Seda', 'Cuero / Piel', 'Denim / Vaquero', 'Otro'];
export const TALLAS_CALZADO = ['30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41', '42', '43', '44', '45'];
export const MATERIALES_JOYERIA = ['Oro Amarillo 18K', 'Oro Blanco 18K', 'Oro Rosa 18K', 'Plata de Ley (925)', 'Acero Inoxidable', 'Latón Bañado', 'Cuero'];
export const PIEDRAS_JOYERIA = ['Sin piedra', 'Circonita Cúbica', 'Cristal', 'Diamante', 'Esmeralda', 'Rubí', 'Zafiro', 'Perla', 'Otra'];
export const COLORES_PIEDRA = ['Blanco / Transparente', 'Azul', 'Verde', 'Rojo', 'Rosa', 'Multicolor', 'Negro'];

export const ATRIBUTOS_POR_TIPO: Record<string, any[]> = {
    ropa_superior: [{ nombre: 'talla', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'sisa_a_sisa_cm', tipo: 'number' }, { nombre: 'hombros_cm', tipo: 'number' }, { nombre: 'largo_total_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    ropa_inferior: [{ nombre: 'talla', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'cintura_cm', tipo: 'number' }, { nombre: 'cadera_cm', tipo: 'number' }, { nombre: 'largo_pierna_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    calzado: [{ nombre: 'numero', tipo: 'select', opciones: TALLAS_CALZADO }, { nombre: 'longitud_plantilla_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: ['Cuero', 'Sintético', 'Lona', 'Goma'] }],
    bolsos: [{ nombre: 'ancho_cm', tipo: 'number' }, { nombre: 'alto_cm', tipo: 'number' }, { nombre: 'profundidad_cm', tipo: 'number' }, { nombre: 'material', tipo: 'select', opciones: ['Cuero', 'Lona', 'Sintético'] }],
    joyeria_anillos: [{ nombre: 'talla_anillo', tipo: 'text' }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_JOYERIA }, { nombre: 'piedra', tipo: 'select', opciones: PIEDRAS_JOYERIA }, { nombre: 'color_piedra', tipo: 'select', opciones: COLORES_PIEDRA }],
    joyeria_general: [{ nombre: 'material', tipo: 'select', opciones: MATERIALES_JOYERIA }, { nombre: 'piedra', tipo: 'select', opciones: PIEDRAS_JOYERIA }, { nombre: 'color_piedra', tipo: 'select', opciones: COLORES_PIEDRA }],
    perfumeria: [{ nombre: 'capacidad_ml', tipo: 'number' }, { nombre: 'concentracion', tipo: 'select', opciones: ['EDT', 'EDP', 'Parfum'] }],
    accesorios: [{ nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }, { nombre: 'dimensiones_notas', tipo: 'text' }],
    guantes: [{ nombre: 'talla_guantes', tipo: 'select', opciones: TALLAS_ROPA }, { nombre: 'material', tipo: 'select', opciones: MATERIALES_ROPA }],
    belleza: [{ nombre: 'cantidad_ml_g', tipo: 'number' }, { nombre: 'formato', tipo: 'text' }]
};

export const MAPEO_IDENTIDAD_POR_TIPO: Record<string, string> = {
    joyeria_anillos: 'material',
    joyeria_collares: 'material',
    joyeria_general: 'material',
    perfumeria: 'capacidad_ml',
    belleza: 'cantidad_ml_g'
};