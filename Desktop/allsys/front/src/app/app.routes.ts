import { Routes } from '@angular/router';
import { LayoutComponent } from './layout/layout.component';
import { LoginComponent } from './features/auth/login/login.component';
import { DashboardComponent } from './features/dashboard/dashboard.component';
import { authGuard } from './core/guards/auth.guard';
import { AddProductComponent } from './features/products/add-product/add-product.component';
import { ProductsListComponent } from './features/products/products-list/products-list.component';
import { ProductDetailComponent } from './features/products/product-detail/product-detail.component';
import { StockDetailComponent } from './features/products/stock-detail/stock-detail.component';
import { EditStockComponent } from './features/products/edit-stock/edit-stock.component';
import { PapeleraComponent } from './features/products/papelera/papelera.component';

import { PosComponent } from './features/pos/pos-create/pos.component';
import { EditSaleComponent } from './features/pos/edit-sale/edit-sale.component';
import { SalesListComponent } from './features/pos/sales-list/sales-list.component';
import { GastosListComponent } from './features/gastos/gastos-list/gastos-list.component';
import { GastosCreateComponent } from './features/gastos/gastos-create/gastos-create.component';
import { StatisticsComponent } from './features/statistics/statistics.component';

// ✨ NUEVAS IMPORTACIONES DEL CRM DE CLIENTES ✨
// (Ajusta estas rutas dependiendo de en qué carpeta generaste los componentes)
import { ListClientsComponent } from './features/clients/list-clients/list-clients.component';
import { EditClientsComponent } from './features/clients/edit-clients/edit-clients.component';
import { AddClientsComponent } from './features/clients/add-clients/add-clients.component';

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
      
      // --- PRODUCTOS ---
      { path: 'new', component: AddProductComponent },
      { path: 'edit/:id', component: AddProductComponent },
      { path: 'view-products', component: ProductsListComponent },
      { path: 'detail-product/:id', component: ProductDetailComponent },
      { path: 'stock-detail/:id', component: StockDetailComponent },
      { path: 'edit-stock/:id', component: EditStockComponent },
      { path: 'papelera', component: PapeleraComponent },

      // --- VENTAS (POS) ---
      { path: 'pos', component: PosComponent },
      { path: 'sales-list', component: SalesListComponent },
      { path: 'edit-sale/:id', component: EditSaleComponent },

      // --- GASTOS ---
      { path: 'gastos', component: GastosListComponent },
      { path: 'gastos/nuevo', component: GastosCreateComponent },
      { path: 'gastos/editar/:id', component: GastosCreateComponent },

      // --- ESTADÍSTICAS ---
      { path: 'statistics', component: StatisticsComponent },

      // ✨ --- CLIENTES CRM --- ✨
      { path: 'clientes', component: ListClientsComponent },
      { path: 'clientes/nuevo', component: AddClientsComponent },
      { path: 'clientes/editar/:id', component: AddClientsComponent },
    ],
  },

  // Si no existe, redirigir al login
  { path: '**', redirectTo: 'login' },
];