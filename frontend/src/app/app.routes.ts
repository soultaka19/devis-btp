import { Routes } from '@angular/router';
import { authGuard } from './core/auth/auth.guard';

export const routes: Routes = [
  {
    path: 'auth',
    loadChildren: () => import('./features/auth/auth.routes').then(m => m.AUTH_ROUTES),
  },
  {
    path: 'dashboard',
    canActivate: [authGuard],
    loadChildren: () => import('./features/dashboard/dashboard.routes').then(m => m.DASHBOARD_ROUTES),
  },
  {
    path: 'quote',
    canActivate: [authGuard],
    loadChildren: () => import('./features/quote/quote.routes').then(m => m.QUOTE_ROUTES),
  },
  {
    path: 'company',
    canActivate: [authGuard],
    loadChildren: () => import('./features/company/company.routes').then(m => m.COMPANY_ROUTES),
  },
  {
    path: 'demo',
    loadChildren: () => import('./features/demo/demo.routes').then(m => m.DEMO_ROUTES),
  },
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: 'dashboard' },
];
