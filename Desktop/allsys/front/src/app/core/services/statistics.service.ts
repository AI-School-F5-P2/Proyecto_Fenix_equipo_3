import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';// Asegúrate de tener tu URL base aquí

@Injectable({
  providedIn: 'root'
})
export class StatisticsService {
  // Ajusta la URL según tu configuración de entorno
  private apiUrl = `http://localhost:8000/api/v1/stats`; 

  constructor(private http: HttpClient) {}

  /**
   * Obtiene el set completo de estadísticas avanzadas.
   * @param fechaInicio Formato 'YYYY-MM-DD'
   * @param fechaFin Formato 'YYYY-MM-DD'
   */
  getDashboardCompleto(fechaInicio?: string, fechaFin?: string): Observable<any> {
    let params = new HttpParams();

    if (fechaInicio) {
      params = params.set('fecha_inicio', fechaInicio);
    }
    if (fechaFin) {
      params = params.set('fecha_fin', fechaFin);
    }

    return this.http.get<any>(`${this.apiUrl}/dashboard-completo`, { params });
  }

  /**
   * (Opcional) Si en el futuro quieres un reporte específico solo de productos,
   * puedes añadir más métodos aquí siguiendo el mismo patrón.
   */
}