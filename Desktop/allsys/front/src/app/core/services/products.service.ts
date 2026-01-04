import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ProductsService {

  private apiUrl = 'http://localhost:8000';

  // 🧠 CACHES
  private categoriasCache: any[] = [];
  private marcasCache: any[] = [];

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

  // ---------------- PRODUCTOS ----------------
  crearProducto(formData: FormData): Observable<any> {
    return this.http.post(`${this.apiUrl}/productos/`, formData);
  }

  obtenerProducto(id: number): Observable<any> {
    return this.http.get(`${this.apiUrl}/productos/${id}`);
  }

  obtenerProductos(pagina: number = 1, offset: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/productos?limit=10&offset=${offset}`);
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
    return this.http.put(
      `${this.apiUrl}/variantes/${varianteId}`,
      data
    );
  }


  // ---------------- EDITAR PRODUCTO (JSON) ----------------
  editarProducto(productoId: number, data: {
    nombre?: string;
    descripcion?: string;
    precio?: number;
    categoria_id?: number;
    marca_id?: number;
    tipo?: string;
  }): Observable<any> {
    return this.http.put(
      `${this.apiUrl}/productos/${productoId}`,
      data
    );
  }








  // ---------------- IMÁGENES ----------------
  agregarImagenesVariante(varianteId: number, formData: FormData): Observable<any> {
  return this.http.post(
    `${this.apiUrl}/variantes/${varianteId}/imagenes`,
    formData
  );
}

  eliminarImagenVariante(imagenId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/imagenes/${imagenId}`);
  }
}
