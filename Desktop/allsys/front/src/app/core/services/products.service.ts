import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
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
}
