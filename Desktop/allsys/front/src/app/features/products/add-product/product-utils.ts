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

  // Obtenemos los nombres de las categorías en la ruta y los pasamos a minúsculas
  const nombreRaiz = ruta[0].nombre.toLowerCase();
  const nombreNivel2 = ruta.length > 1 ? ruta[1].nombre.toLowerCase() : '';
  const nombreNivel3 = ruta.length > 2 ? ruta[2].nombre.toLowerCase() : '';

  // 1. CALZADO (Aplica para hombre, mujer, niños y bebé)
  if (nombreRaiz === 'calzado') {
    return 'calzado';
  }

  // 2. BOLSOS
  if (nombreRaiz === 'bolsos') {
    return 'bolsos';
  }

  // 3. ACCESORIOS (Anillos, guantes o general)
  if (nombreRaiz === 'accesorios') {
    // Si quisieras ser muy específico con la joyería (ej. para pedir talla de anillo):
    if (nombreNivel3.includes('joyeria') || nombreNivel3.includes('anillos')) {
      return 'joyeria_anillos';
    }
    if (nombreNivel3.includes('guantes')) {
      return 'guantes';
    }
    return 'accesorios';
  }

  // 4. ROPA
  if (nombreRaiz === 'ropa') {
    // Si no han seleccionado subcategoría, asumimos superior por defecto
    if (!nombreNivel3) return 'ropa_superior';

    // Lista de palabras clave que identifican ropa INFERIOR
    const palabrasInferior = [
      'falda', 'faldas', 'pantalón', 'pantalones', 'vaquero', 'vaqueros',
      'short', 'shorts', 'bermudas', 'leggins', 'leggings', 'chinos',
      'joggers', 'braguitas', 'polainas', 'culetines', 'calzoncillos'
    ];

    // Comprobamos si el nombre de la subcategoría (nivel 3) incluye alguna palabra de ropa inferior
    const esInferior = palabrasInferior.some(palabra => nombreNivel3.includes(palabra));

    if (esInferior) {
      return 'ropa_inferior';
    }

    // Si es un vestido, mono, abrigo, etc., y no es inferior, entonces es superior/cuerpo entero
    return 'ropa_superior';
  }

  return 'accesorios';
}

// Opcional: Una función extra que te puede ser muy útil para el formulario
export function determinarGenero(ruta: any[]): string {
  if (!ruta || ruta.length === 0) return 'unisex';
  
  // Como tu backend ahora envía el "genero", simplemente lo buscamos en el último nodo seleccionado
  const ultimoNodo = ruta[ruta.length - 1];
  
  if (ultimoNodo && ultimoNodo.genero) {
    return ultimoNodo.genero; // Devolverá "mujer", "hombre", "niño", "niña" o "bebé"
  }
  
  return 'unisex';
}