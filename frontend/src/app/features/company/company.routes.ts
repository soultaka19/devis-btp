import { Routes } from '@angular/router';

export const COMPANY_ROUTES: Routes = [
  {
    path: '',
    loadComponent: () =>
      import('./components/settings/company-settings.component').then(m => m.CompanySettingsComponent),
  },
];
