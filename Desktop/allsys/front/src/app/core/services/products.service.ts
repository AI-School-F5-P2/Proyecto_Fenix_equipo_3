import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { ProductoBackend } from '../../features/products/add-product/add-product.component';

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
  cargarCategorias(): Observable<any[]> {
    if (this.categoriasCache.length > 0) {
      return new Observable(observer => {
        observer.next(this.categoriasCache);
        observer.complete();
      });
    }
    return this.http.get<any[]>(`${this.apiUrl}/categorias`).pipe(
      tap(data => this.categoriasCache = data)
    );
  }

  getCategoriasPadre(): any[] {
    return this.categoriasCache.filter(c => c.parent_id === null);
  }

  getSubcategorias(parentId: number): any[] {
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

  obtenerProductos(page: number = 1, limit: number = 10): Observable<PaginatedResponse> {
    // Fíjate que cambiamos <any[]> por <PaginatedResponse>
    // Y actualizamos los parámetros para usar 'page' y 'limit'
    return this.http.get<PaginatedResponse>(`${this.apiUrl}/productos?page=${page}&limit=${limit}`);
  }

  // ---------------- ACTUALIZAR PRODUCTO ----------------
  actualizarProducto(productoId: number, formData: FormData): Observable<any> {
    return this.http.put(`${this.apiUrl}/productos/${productoId}`, formData);
  }

  // ---------------- ELIMINAR PRODUCTO ----------------
  eliminarProducto(productoId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/productos/${productoId}`);
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