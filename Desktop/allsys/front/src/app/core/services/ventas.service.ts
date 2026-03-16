import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class VentasService {

  private API_URL = 'http://localhost:8000/api/v1/auth';

  constructor(private http: HttpClient) {}

  // 🔎 Buscar producto por TALLA
  buscarProductoPorTalla(talla_id: number): Observable<any> {
    return this.http.get<any>(
      `${this.API_URL}/ventas/producto/${talla_id}`
    );
  }

  // 💾 Registrar venta
  registrarVenta(data: {
    variante_id: number;
    talla_id: number;
    cantidad: number;
    precio_venta: number;
    fecha: string;
    canal: string;
    vendedor: string;
    comprador?: string;
  }): Observable<any> {

    const formData = new FormData();

    formData.append('variante_id', String(data.variante_id));
    formData.append('talla_id', String(data.talla_id));
    formData.append('cantidad', String(data.cantidad));
    formData.append('precio_venta', String(data.precio_venta));
    formData.append('fecha', data.fecha);
    formData.append('canal', data.canal);
    formData.append('vendedor', data.vendedor);

    if (data.comprador && data.comprador.trim() !== '') {
      formData.append('comprador', data.comprador);
    }

    return this.http.post(
      `${this.API_URL}/ventas/`,
      formData
    );
  }
}
