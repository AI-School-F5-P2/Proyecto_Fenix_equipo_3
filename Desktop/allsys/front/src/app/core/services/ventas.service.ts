import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

// Definimos interfaces para que tu código sea robusto y tengas autocompletado
export interface DetalleVenta {
  stock_id: number;
  cantidad: number;
  precio_unitario: number;
}

export interface VentaData {
  fecha?: string;
  canal: string;          // 'web' | 'tienda' | 'vinted' | 'wallapop'
  vendedor: string;       // 'Yenny' | 'Maikol' | 'Paola'
  metodo_pago: string;    // 'efectivo' | 'tarjeta' | 'stripe'
  nombre_cliente?: string;
  email_cliente?: string;
  costo_envio?: number;
  descuento_total?: number;
  transaccion_id_externo?: string;
  detalles: DetalleVenta[]; // El "carrito"
}

@Injectable({
  providedIn: 'root'
})
export class VentasService {

  // ⚠️ Corregido: Quitamos '/auth' de la URL base para ventas
  private API_URL = 'http://localhost:8000/api/v1/ventas';

  constructor(private http: HttpClient) {}

  /**
   * 🔎 Buscar producto por ID de Stock (Talla específica)
   * Útil para cuando escanean o buscan una prenda exacta
   */
  buscarProductoPorStock(stockId: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/producto/${stockId}`);
  }

  /**
   * 💰 Registrar una venta completa
   * Ahora enviamos un JSON plano, Angular se encarga del resto
   */
  registrarVenta(data: VentaData): Observable<any> {
    // Ya no hace falta crear un FormData. 
    // Enviamos el objeto 'data' directamente como segundo parámetro.
    return this.http.post<any>(`${this.API_URL}/`, data);
  }

  /**
   * 📄 Obtener historial de ventas (Opcional, para el futuro)
   */
  // listarVentas(page: number = 1, limit: number = 10): Observable<any> {
  //   return this.http.get<any>(`${this.API_URL}/?page=${page}&limit=${limit}`);
  // }


  // 📄 Obtener historial de ventas con filtros
  listarVentas(
    page: number, limit: number, search?: string, 
    estado?: string, canal?: string, fechaInicio?: string, 
    fechaFin?: string, vendedor?: string, comprador?: string // 👈 Agregados
  ): Observable<any> {
    let params = `?page=${page}&limit=${limit}`;
    if (search) params += `&search=${search}`;
    if (estado) params += `&estado=${estado}`;
    if (canal) params += `&canal=${canal}`;
    if (fechaInicio) params += `&fecha_inicio=${fechaInicio}`; // 👈 NUEVO
    if (fechaFin) params += `&fecha_fin=${fechaFin}`;
    if (vendedor) params += `&vendedor=${vendedor}`;    // 👈
    if (comprador) params += `&comprador=${comprador}`;

    return this.http.get<any>(`${this.API_URL}/${params}`);
  }

  // 📄 Obtener detalle de una venta
  obtenerVenta(ventaId: number): Observable<any> {
    return this.http.get<any>(`${this.API_URL}/detalle/${ventaId}`);
  }

  // 📝 Editar venta
  editarVenta(ventaId: number, data: any): Observable<any> {
    return this.http.put<any>(`${this.API_URL}/${ventaId}`, data);
  }
}