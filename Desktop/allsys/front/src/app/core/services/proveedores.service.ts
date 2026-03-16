import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class SuppliersService {

  private apiUrl = 'http://localhost:8000/api/v1/proveedores';
  private proveedoresCache: any[] = [];

  constructor(private http: HttpClient) {}

  /**
   * Carga la lista de proveedores (con caché)
   */
  getProveedores(): Observable<any[]> {
    if (this.proveedoresCache.length > 0) {
      return of(this.proveedoresCache);
    }
    return this.http.get<any[]>(this.apiUrl).pipe(
      tap(data => this.proveedoresCache = data)
    );
  }

  /**
   * Fuerza la actualización de la lista (ignora caché)
   */
  refrescarProveedores(): Observable<any[]> {
    return this.http.get<any[]>(this.apiUrl).pipe(
      tap(data => this.proveedoresCache = data)
    );
  }

  /**
   * Crea un nuevo proveedor
   * @param nombre Nombre del proveedor
   */
  crearProveedor(nombre: string): Observable<any> {
    // Usamos params porque en el backend definimos 'nombre: str' como query param
    return this.http.post(`${this.apiUrl}/`, null, {
      params: { nombre: nombre }
    }).pipe(
      tap(() => this.proveedoresCache = []) // Limpiamos caché para que se actualice la lista
    );
  }

  /**
   * Actualiza un proveedor existente
   */
  actualizarProveedor(id: number, nuevoNombre: string): Observable<any> {
    return this.http.put(`${this.apiUrl}/${id}`, null, {
      params: { nombre: nuevoNombre }
    }).pipe(
      tap(() => this.proveedoresCache = [])
    );
  }

  /**
   * Elimina un proveedor
   */
  eliminarProveedor(id: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/${id}`).pipe(
      tap(() => this.proveedoresCache = [])
    );
  }
}