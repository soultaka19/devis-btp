import { Routes } from '@angular/router';

export const DEMO_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./demo-entry.component').then((m) => m.DemoEntryComponent),
  },
];
