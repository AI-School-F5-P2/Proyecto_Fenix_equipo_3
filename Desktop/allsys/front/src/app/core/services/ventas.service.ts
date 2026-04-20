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
  canal: string;          
  vendedor: string;       
  metodo_pago: string;    
  estado_venta: string;   // 👈 NUEVO
  estado_pago: string;    // 👈 NUEVO
  nombre_cliente?: string;
  email_cliente?: string;
  costo_envio?: number;
  descuento_total?: number;
  transaccion_id_externo?: string;
  empresa_transporte?: string; // 👈 NUEVO
  numero_seguimiento?: string; // 👈 NUEVO
  detalles: DetalleVenta[]; 
  identificador_cliente?: string; // <-- AÑADIR ESTA LÍNEA
  tipo_identificador?: string;
  prefijo_telefono?: string;
  tipo_documento?: string;
  pais?: string;
  apellidos_cliente?: string;
 
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


  obtenerConteoCompras(identificador: string): Observable<{compras_totales: number}> {
  return this.http.get<{compras_totales: number}>(`${this.API_URL}/historial-cliente/${identificador}`);
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
  // 📄 Obtener historial de ventas con filtros
  // 📄 Obtener historial de ventas con filtros
  listarVentas(
    page: number, limit: number, 
    searchProducto?: string, tipoBusquedaProd?: string, 
    searchCodigo?: string, 
    searchCliente?: string, tipoBusquedaCliente?: string, // ✨ NUEVOS
    estado?: string, canal?: string, fechaInicio?: string, fechaFin?: string, 
    vendedor?: string, marca_id?: string, categoria_id?: number
  ): Observable<any> {
    let params = `?page=${page}&limit=${limit}`;
    
    if (searchProducto) params += `&search_producto=${searchProducto}`;
    if (tipoBusquedaProd) params += `&tipo_busqueda_prod=${tipoBusquedaProd}`;
    if (searchCodigo) params += `&search_codigo=${searchCodigo}`;
    
    if (searchCliente) params += `&search_cliente=${searchCliente}`;
    if (tipoBusquedaCliente) params += `&tipo_busqueda_cliente=${tipoBusquedaCliente}`;

    if (estado) params += `&estado=${estado}`;
    if (canal) params += `&canal=${canal}`;
    if (fechaInicio) params += `&fecha_inicio=${fechaInicio}`; 
    if (fechaFin) params += `&fecha_fin=${fechaFin}`;
    if (vendedor) params += `&vendedor=${vendedor}`;    
    if (marca_id) params += `&marca_id=${marca_id}`;
    if (categoria_id) params += `&categoria_id=${categoria_id}`;

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