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

    if (filtros.search?.trim()) {
      params = params.set('search', filtros.search.trim());
      if (filtros.tipo_busqueda) params = params.set('tipo_busqueda', filtros.tipo_busqueda);
    }
    
    if (filtros.categoria_id) params = params.set('categoria_id', filtros.categoria_id.toString());
    if (filtros.marca_id) params = params.set('marca_id', filtros.marca_id.toString());
    if (filtros.estado) params = params.set('estado', filtros.estado);
    if (filtros.precio_min !== null) params = params.set('precio_min', filtros.precio_min.toString());
    if (filtros.precio_max !== null) params = params.set('precio_max', filtros.precio_max.toString());
    if (filtros.ordenar_por) params = params.set('ordenar_por', filtros.ordenar_por);
    if (filtros.color) params = params.set('color', filtros.color);
    if (filtros.talla) params = params.set('talla', filtros.talla);
    if (filtros.fecha_inicio) params = params.set('fecha_inicio', filtros.fecha_inicio);
    if (filtros.fecha_fin) params = params.set('fecha_fin', filtros.fecha_fin);

    if (filtros.proveedores_ids && filtros.proveedores_ids.length > 0) {
      filtros.proveedores_ids.forEach((id: number) => {
        params = params.append('proveedores_ids', id.toString());
      });
    }

    return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos/`, { params });
  }

  obtenerInventarioIndividual(pagina: number, limite: number, filtros: any): Observable<PaginatedResponse> {
  
    let params = new HttpParams()
      .set('page', pagina.toString())
      .set('limit', limite.toString());

    if (filtros.search?.trim()) {
      params = params.set('search', filtros.search.trim());
      if (filtros.tipo_busqueda) params = params.set('tipo_busqueda', filtros.tipo_busqueda);
    }
    
    if (filtros.categoria_id) params = params.set('categoria_id', filtros.categoria_id.toString());
    if (filtros.marca_id) params = params.set('marca_id', filtros.marca_id.toString());
    if (filtros.color) params = params.set('color', filtros.color);
    if (filtros.talla) params = params.set('talla', filtros.talla);
    if (filtros.estado) params = params.set('estado', filtros.estado);
    if (filtros.precio_min !== null && filtros.precio_min !== undefined) params = params.set('precio_min', filtros.precio_min.toString());
    if (filtros.precio_max !== null && filtros.precio_max !== undefined) params = params.set('precio_max', filtros.precio_max.toString());
    if (filtros.ordenar_por) params = params.set('ordenar_por', filtros.ordenar_por);
    if (filtros.fecha_inicio) params = params.set('fecha_inicio', filtros.fecha_inicio);
    if (filtros.fecha_fin) params = params.set('fecha_fin', filtros.fecha_fin);

    if (filtros.proveedores_ids && filtros.proveedores_ids.length > 0) {
      filtros.proveedores_ids.forEach((id: number) => {
        params = params.append('proveedores_ids', id.toString());
      });
    }

    return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos/inventario-individual`, { params });
  }
  

  // ---------------- ACTUALIZAR PRODUCTO ----------------
  actualizarProducto(productoId: number, formData: FormData): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/${productoId}`, formData);
  }


 // ---------------- GESTIÓN DE PAPELERA ----------------
  
  // 1. Envía el producto a la papelera (Soft Delete)
  moverProductoPapelera(productoId: number): Observable<any> {
    // Fíjate que ahora es un PUT y la URL incluye "/papelera"
    return this.http.put(`${this.apiUrl}/productos/${productoId}/papelera`, {});
  }

  // 2. Destruye el producto permanentemente (Hard Delete)
  destruirProducto(productoId: number): Observable<any> {
    // Esta ruta la usarás más adelante cuando construyas la vista de la "Papelera"
    return this.http.delete(`${this.apiUrl}/productos/papelera/${productoId}`);
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
}