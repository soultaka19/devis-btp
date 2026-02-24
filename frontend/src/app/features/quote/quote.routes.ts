import { Routes } from '@angular/router';

export const QUOTE_ROUTES: Routes = [
  {
    path: 'new',
    loadComponent: () =>
      import('./components/compose/quote-compose.component').then(m => m.QuoteComposeComponent),
  },
  {
    path: ':id',
    loadComponent: () =>
      import('./components/compose/quote-compose.component').then(m => m.QuoteComposeComponent),
  },
];
