import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
 // Ajusta la ruta a tu env

export interface ClienteData {
  id?: number;
  email?: string;
  telefono?: string;
  usuario_vinted?: string;
  usuario_wallapop?: string;
  nombre?: string;
  apellidos?: string;
  dni_nie?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  provincia?: string;
  pais?: string;
  notas_internas?: string;
  es_vip?: boolean;
  total_ventas?: number;
  fecha_registro?: string;
}

// Campos base
export interface ClienteBase {
  nombre: string;
  apellidos?: string;
  email?: string;
  telefono?: string;
  usuario_vinted?: string;
  usuario_wallapop?: string;
  dni_nie?: string;
  direccion?: string;
  ciudad?: string;
  codigo_postal?: string;
  provincia?: string;
  pais: string;
  notas_internas?: string;
  es_vip: boolean;
}

// Para CREAR y EDITAR (No necesitamos el ID dentro del objeto enviado)
export interface ClienteCreate extends ClienteBase {}

// Para LEER (Lo que viene del servidor con ID y cálculos)
export interface ClienteRead extends ClienteBase {
  id: number;
  total_ventas: number;
}

@Injectable({
  providedIn: 'root'
})
export class ClientesService {
  private apiUrl = `http://localhost:8000/api/v1/clientes`;

  constructor(private http: HttpClient) {}

  obtenerClientes(filtros: any): Observable<any> {
    let params = new HttpParams()
      .set('page', filtros.page || 1)
      .set('limit', filtros.limit || 10);

    if (filtros.search) params = params.set('search', filtros.search);
    if (filtros.pais) params = params.set('pais', filtros.pais);
    if (filtros.fecha_inicio) params = params.set('fecha_inicio', filtros.fecha_inicio);
    if (filtros.fecha_fin) params = params.set('fecha_fin', filtros.fecha_fin);

    return this.http.get<any>(`${this.apiUrl}/`, { params });
  }

  
  actualizarCliente(id: number, data: ClienteData): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/${id}`, data);
  }
  crearCliente(data: ClienteData): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/`, data);
  }

  obtenerClientePorId(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/${id}`);
  }

  desactivarCliente(id: number): Observable<any> {
    // Usamos patch para ser fieles a la semántica del backend
    return this.http.patch<any>(`${this.apiUrl}/${id}/desactivar`, {});
  }
}