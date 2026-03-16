import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

interface LoginRequest {
  email: string;
  password: string;
}

interface RegisterRequest {
  nombre: string;
  email: string;
  password: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiUrl = 'http://localhost:8000/api/v1/auth'; // 🔹 URL base del backend FastAPI

  constructor(private http: HttpClient) {}

  // ✅ Registro de usuario
  register(data: RegisterRequest): Observable<any> {
    return this.http.post(`${this.apiUrl}/register`, data);
  }

  // ✅ Inicio de sesión
  login(data: LoginRequest): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${this.apiUrl}/login`, data).pipe(
      tap((response) => {
        // Guardamos el token en localStorage para usarlo luego
        localStorage.setItem('access_token', response.access_token);
      })
    );
  }

  // ✅ Cerrar sesión
  logout(): void {
    localStorage.removeItem('access_token');
  }

  // ✅ Obtener token
  getToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // ✅ Saber si el usuario está logueado
  isLoggedIn(): boolean {
    return !!this.getToken();
  }
}
