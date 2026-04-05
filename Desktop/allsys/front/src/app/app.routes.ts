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

// 👇 Importa el nuevo componente (ajusta la ruta según dónde lo hayas generado)
import { PosComponent } from './features/pos/pos.component';

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
      { path: 'new', component: AddProductComponent },
      { path: 'edit/:id', component: AddProductComponent },
      { path: 'view-products', component: ProductsListComponent },
      { path: 'detail-product/:id', component: ProductDetailComponent },
      { path: 'stock-detail/:id', component: StockDetailComponent },
      { path: 'edit-stock/:id', component: EditStockComponent },
      { path: 'papelera', component: PapeleraComponent },
      
      // ✨ NUEVA RUTA PARA EL PUNTO DE VENTA (TPV / CAJA)
      { path: 'pos', component: PosComponent },
    ],
  },

  // Si no existe, redirigir al login
  { path: '**', redirectTo: 'login' },
];