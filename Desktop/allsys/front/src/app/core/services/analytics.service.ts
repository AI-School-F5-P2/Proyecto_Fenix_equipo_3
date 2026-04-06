import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AnalyticsService {
  // 1. La URL base debe llegar hasta el prefijo del router
  private API_URL = 'http://localhost:8000/api/v1/analytics';

  constructor(private http: HttpClient) {}

  // obtenerResumenFinanciero(
  //   fechaInicio?: string, 
  //   fechaFin?: string, 
  //   vendedor?: string, 
  //   canal?: string
  // ): Observable<any> {
    
  //   // 2. Usamos HttpParams para manejar los query strings de forma segura
  //   let params = new HttpParams();

  //   if (fechaInicio) params = params.set('fecha_inicio', fechaInicio);
  //   if (fechaFin) params = params.set('fecha_fin', fechaFin);
  //   if (vendedor) params = params.set('vendedor', vendedor);
  //   if (canal) params = params.set('canal', canal);

  //   // 3. La ruta final será: .../api/v1/analytics/financiero
  //   return this.http.get<any>(`${this.API_URL}/financiero`, { params });
  // }

  getDashboardCompleto(fInicio: string, fFin: string) {
  return this.http.get(`${this.API_URL}/dashboard-completo?fecha_inicio=${fInicio}&fecha_fin=${fFin}`);
}
}