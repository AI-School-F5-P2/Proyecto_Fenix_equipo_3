import { Routes } from '@angular/router';

import { LayoutComponent } from './layout/layout.component';

import { LoginComponent } from './features/auth/login/login.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { authGuard } from './core/guards/auth.guard';
import { AddProductComponent } from './features/products/add-product/add-product.component';

export const routes: Routes = [
  // Ruta pública (login)
  { path: 'login', component: LoginComponent },

  // Rutas protegidas (dashboard, etc.)
  {
    path: '',
    component: LayoutComponent,
    canActivate: [authGuard], // 👈 proteger con el guard
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'add-product', component: AddProductComponent },
    ],
  },

  // Si no existe, redirigir al login
  { path: '**', redirectTo: 'login' },
];
