import { Injectable, inject } from '@angular/core';
import { ApiService } from '../../../core/api/api.service';
import { DashboardStats } from '../models/dashboard.model';

@Injectable({ providedIn: 'root' })
export class DashboardApiService {
  private api = inject(ApiService);

  getStats() { return this.api.get<DashboardStats>('/dashboard/stats'); }
  getRecent(limit = 10) { return this.api.get<any[]>(`/dashboard/recent?limit=${limit}`); }
}
