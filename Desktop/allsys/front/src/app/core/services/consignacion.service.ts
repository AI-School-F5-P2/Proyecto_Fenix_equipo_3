import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EstadisticasConsignacion {
  total_prendas_entregadas: number;
  prendas_vendidas: number;
  prendas_en_stock: number;
  // ✨ NUEVOS CAMPOS AÑADIDOS
  prendas_devueltas: number;
  prendas_donadas: number;
  prendas_extraviadas: number;
  exento_gastos_gestion: boolean;
  deuda_por_devoluciones: number;
  // FIN NUEVOS CAMPOS
  dinero_generado_ventas: number;
  dinero_para_cliente: number;
  beneficio_plataforma: number;
  dinero_ya_pagado: number;
  saldo_pendiente: number;
}

export interface PagoCreate {
  monto: number;
  metodo_pago: string;
  referencia?: string | null;
  notas?: string | null;
}

export interface PagoRead extends PagoCreate {
  id: number;
  fecha: string;
}

@Injectable({
  providedIn: 'root'
})
export class ConsignacionService {
  private apiUrl = 'http://localhost:8000/api/v1/consignacion'; 

  constructor(private http: HttpClient) {}

  getStats(clienteId: number): Observable<EstadisticasConsignacion> {
    return this.http.get<EstadisticasConsignacion>(`${this.apiUrl}/cliente/${clienteId}/stats`);
  }

  registrarPago(clienteId: number, data: PagoCreate): Observable<PagoRead> {
    return this.http.post<PagoRead>(`${this.apiUrl}/cliente/${clienteId}/pagar`, data);
  }

  getPagos(clienteId: number): Observable<PagoRead[]> {
    return this.http.get<PagoRead[]>(`${this.apiUrl}/cliente/${clienteId}/pagos`);
  }
}