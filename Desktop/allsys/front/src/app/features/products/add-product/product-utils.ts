// app/pages/products/add-product/product-utils.ts

export function generarTempId(): string {
  return crypto.randomUUID();
}

export function formatLabel(nombre: string): string {
  const diccionario: Record<string, string> = {
    'sisa_a_sisa_cm': 'Sisa a Sisa (cm)',
    'hombros_cm': 'Hombros (cm)',
    'largo_total_cm': 'Largo Total (cm)',
    'cintura_cm': 'Cintura (cm)',
    'cadera_cm': 'Cadera (cm)',
    'largo_pierna_cm': 'Largo Pierna (cm)',
    'longitud_plantilla_cm': 'Plantilla (cm)',
    'capacidad_ml': 'Capacidad (ml)',
    'talla_anillo': 'Talla de Anillo',
    'cantidad_ml_g': 'Contenido (ml/g)'
  };
  return diccionario[nombre] || nombre.replace(/_/g, ' ').toUpperCase();
}

export function getPlaceholder(nombre: string): string {
  if (nombre.includes('_cm')) return '0';
  if (nombre.includes('_ml')) return '100';
  if (nombre === 'material') return 'Ej: Oro 18k, Algodón...';
  return '...';
}
export function determinarTipoBase(ruta: any[]): string {
  if (!ruta || ruta.length === 0) return 'accesorios';

  // Creamos un string con todos los nombres de la ruta en minúsculas para buscar fácilmente
  const nombresRuta = ruta.map(cat => cat.nombre.toLowerCase());
  const nombreRaiz = nombresRuta[0];

  // 1. CALZADO
  if (nombreRaiz.includes('calzado')) return 'calzado';

  // 2. BOLSOS
  if (nombreRaiz.includes('bolsos')) return 'bolsos';

  // 3. JOYERÍA / ANILLOS (Busca en toda la ruta)
  // Ahora detectará "Anillos" aunque sea Nivel 4
  if (nombresRuta.some(n => n.includes('anillos') || n.includes('sortijas'))) {
    return 'joyeria_anillos';
  }

  // 4. GUANTES
  if (nombresRuta.some(n => n.includes('guantes'))) return 'guantes';

  // 5. ROPA (Superior vs Inferior)
  if (nombreRaiz.includes('ropa')) {
    // Lista extendida de palabras clave para partes INFERIORES (incluye niños y bebés)
    const palabrasInferior = [
      'falda', 'pantalón', 'pantalon', 'vaquero', 'short', 'bermuda', 
      'leggin', 'chino', 'jogger', 'braguita', 'polaina', 'culetine', 
      'calzoncillo', 'slip', 'boxer'
    ];

    // Si alguna palabra de la lista está en cualquier parte de la ruta, es inferior
    const esInferior = nombresRuta.some(nombre => 
      palabrasInferior.some(palabra => nombre.includes(palabra))
    );

    if (esInferior) return 'ropa_inferior';

    // Por defecto para ropa (Vestidos, Camisas, Abrigos, Bodys, Peleles)
    return 'ropa_superior';
  }

  // 6. ACCESORIOS GENERAL (Sombreros, gafas, relojes, etc.)
  return 'accesorios';
}

/**
 * Determina el género basándose en la ruta.
 * Prioriza el género más específico encontrado (de derecha a izquierda).
 */
export function determinarGenero(ruta: any[]): string {
  if (!ruta || ruta.length === 0) return 'unisex';
  console.log(ruta)
  // Recorremos la ruta de abajo hacia arriba (lo más específico primero)
  for (let i = ruta.length - 1; i >= 0; i--) {
    if (ruta[i].genero && ruta[i].genero !== 'null') {
      console.log(ruta[i].genero)
      return ruta[i].genero; // Retorna: 'mujer', 'hombre', 'niña', 'niño' o 'bebé'
    }
  }

  return 'unisex';
}

export const MAPEO_IDENTIDAD_POR_TIPO: Record<string, string> = {
    ropa_superior: 'color',
    ropa_inferior: 'color',
    calzado: 'color',
    joyeria_anillos: 'material',
    joyeria_general: 'material',
    perfumeria: 'capacidad_ml',
    accesorios: 'color'
};

export  const MAPEO_MATERIAL_A_COLOR: Record<string, string> = {
  'Oro Amarillo 18K': 'Dorado',
  'Oro Blanco 18K': 'Plateado',
  'Oro Rosa 18K': 'Rosa', // O un color cobre/bronce si tienes en tu paleta
  'Plata de Ley (925)': 'Plateado',
  'Acero Inoxidable': 'Plateado',
  'Latón Bañado': 'Dorado',
  'Cuero': 'Negro', // O marrón
  'Aluminio': 'Plateado',
  'Cobre': 'Burdeos' // Como aproximación a naranja/cobre
};