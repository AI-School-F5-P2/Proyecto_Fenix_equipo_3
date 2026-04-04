import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { Categoria, ProductoBackend } from '../../features/products/add-product/product-form.config';
import { MisFiltros } from '../../features/products/products-list/products-list.component';


export interface PaginatedResponse {
  total: number;
  items: any[];
}

@Injectable({
  providedIn: 'root'
})
export class ProductsService {

  

  private apiUrl = 'http://localhost:8000/api/v1';

  // 🧠 CACHES
  private categoriasCache: any[] = [];
  private marcasCache: any[] = [];
  private proveedoresCache: any[] = [];

  constructor(private http: HttpClient) {}


  private cleanParams(params: HttpParams, filtros: any): HttpParams {
  const llaves = [
    'search', 'tipo_busqueda', 'categoria_id', 'marca_id', 
    'estado', 'precio_min', 'precio_max', 'ordenar_por', 
    'color', 'talla', 'fecha_inicio', 'fecha_fin'
  ];

  llaves.forEach(key => {
    const valor = filtros[key];
    // Solo agregamos si el valor no es nulo, no es la palabra "null" y no es un string vacío
    if (valor !== null && valor !== undefined && valor !== '' && valor !== 'null') {
      params = params.set(key, valor.toString());
    }
    
    if (key === 'disponibilidad' && valor !== 'todos') {
      params = params.set('disponibilidad', valor);
    }
  });

  // Manejo especial de proveedores (arrays)
  if (filtros.proveedores_ids?.length > 0) {
    filtros.proveedores_ids.forEach((id: number) => {
      params = params.append('proveedores_ids', id.toString());
    });
  }
  

  return params;
}

  // ---------------- CATEGORÍAS ----------------
cargarCategorias(): Observable<Categoria[]> { // ✨ Cambiado any[] por Categoria[]
  if (this.categoriasCache.length > 0) {
    return new Observable(observer => {
      observer.next(this.categoriasCache);
      observer.complete();
    });
  }
  return this.http.get<Categoria[]>(`${this.apiUrl}/categorias`).pipe( // ✨ Tipado aquí también
    tap(data => this.categoriasCache = data)
  );
}

getCategoriasPadre(): Categoria[] {
  return this.categoriasCache.filter(c => c.parent_id === null);
}

getSubcategorias(parentId: number): Categoria[] {
  return this.categoriasCache.filter(c => c.parent_id === parentId);
}

  // ---------------- MARCAS ----------------
  cargarMarcas(): Observable<any[]> {
    if (this.marcasCache.length > 0) {
      return new Observable(observer => {
        observer.next(this.marcasCache);
        observer.complete();
      });
    }
    return this.http.get<any[]>(`${this.apiUrl}/marcas`).pipe(
      tap(data => this.marcasCache = data)
    );
  }

  // ---------------- PROVEEDORES ----------------
  cargarProveedores(): Observable<any[]> {
    if (this.proveedoresCache.length > 0) {
      return new Observable(observer => {
        observer.next(this.proveedoresCache);
        observer.complete();
      });
    }
    return this.http.get<any[]>(`${this.apiUrl}/proveedores`).pipe(
      tap(data => this.proveedoresCache = data)
    );
  }

  // ---------------- PRODUCTOS ----------------
  crearProducto(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/productos/`, formData);
  }

  obtenerProducto(id: number): Observable<ProductoBackend> {
  return this.http.get<ProductoBackend>(`${this.apiUrl}/productos/${id}`);
}



obtenerProductos(pagina: number, limite: number, filtros: MisFiltros) {
  let params = new HttpParams()
    .set('page', pagina.toString())
    .set('limit', limite.toString());

  if (filtros.disponibilidad && filtros.disponibilidad !== 'todos') {
    params = params.set('disponibilidad', filtros.disponibilidad);
  }

  params = this.cleanParams(params, filtros);
  return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos/`, { params });
}

obtenerInventarioIndividual(pagina: number, limite: number, filtros: any) {
  let params = new HttpParams()
    .set('page', pagina.toString())
    .set('limit', limite.toString());

  if (filtros.disponibilidad && filtros.disponibilidad !== 'todos') {
    params = params.set('disponibilidad', filtros.disponibilidad);
  }

  params = this.cleanParams(params, filtros);
  return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos/inventario-individual`, { params });
}
  

  // ---------------- ACTUALIZAR PRODUCTO ----------------
  actualizarProducto(productoId: number, formData: FormData): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/${productoId}`, formData);
  }


  // ---------------- VARIANTES ----------------
  editarVariante(
    varianteId: number,
    data: {
      color?: string;
      color_nombre?: string;
      precio?: number;
      descuento?: number;
      tallas?: { id: number; stock: number }[];
    }
  ): Observable<any> {
    return this.http.put(`${this.apiUrl}/variantes/${varianteId}`, data);
  }




// En tu products.service.ts
obtenerStock(id: number): Observable<any> {
  return this.http.get<any>(`${this.apiUrl}/productos/stock/${id}`);
}


// En tu products.service.ts
  actualizarStockIndividual(id: number, payload: any): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/stock/${id}`, payload);
  }




  // ---------------- EDITAR PRODUCTO (JSON) ----------------
 editarProducto(id: number, formData: FormData) {
    // ✨ LOG ESPÍA DEL SERVICE ✨
    console.log(`=== ENVIANDO AL BACKEND (PUT /productos/${id}) ===`);
    
    // Recorremos el FormData para imprimir cada llave y su valor
    formData.forEach((value, key) => {
      // Si la llave es 'variantes', la convertimos de texto a JSON para leerla mejor
      if (key === 'variantes') {
        console.log(`📦 ${key}:`, JSON.parse(value as string));
      } else {
        console.log(`🔑 ${key}:`, value);
      }
    });
    
    console.log(`====================================================`);

    return this.http.put(`${this.apiUrl}/productos/${id}`, formData);
  }
  // ---------------- IMÁGENES ----------------
  agregarImagenesVariante(varianteId: number, formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/variantes/${varianteId}/imagenes`, formData);
  }

  eliminarImagenVariante(imagenId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/imagenes/${imagenId}`);
  }




  // ========================================================
  // 🗑️ GESTIÓN DE PAPELERA (PRODUCTOS, VARIANTES Y STOCKS)
  // ========================================================

  // --- 1. OBTENER LISTADO DE PAPELERA ---
  obtenerPapelera(pagina: number = 1, limite: number = 10): Observable<PaginatedResponse> {
    const params = new HttpParams()
      .set('page', pagina.toString())
      .set('limit', limite.toString());
    return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos/papelera`, { params });
  }

  // --- 2. MOVER A PAPELERA (SOFT DELETE) ---
  moverProductoPapelera(productoId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/${productoId}/papelera`, {});
  }

  moverVariantePapelera(varianteId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/variante/${varianteId}/papelera`, {});
  }

  moverStockPapelera(stockId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/stock/${stockId}/papelera`, {});
  }

  // --- 3. RESTAURAR DE PAPELERA ---
  restaurarProducto(productoId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/${productoId}/restaurar`, {});
  }

  restaurarVariante(varianteId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/variante/${varianteId}/restaurar`, {});
  }

  restaurarStock(stockId: number): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/stock/${stockId}/restaurar`, {});
  }

  // --- 4. DESTRUCCIÓN TOTAL (HARD DELETE) ---
  destruirProducto(productoId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/productos/papelera/${productoId}`);
  }

  destruirVariante(varianteId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/productos/papelera/variante/${varianteId}`);
  }

  destruirStock(stockId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/productos/papelera/stock/${stockId}`);
  }
  // ========================================================
}