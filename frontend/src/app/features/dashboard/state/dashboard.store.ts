import { Injectable, inject, signal } from '@angular/core';
import { DashboardStats } from '../models/dashboard.model';
import { DashboardApiService } from '../services/dashboard-api.service';
import { forkJoin } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DashboardStore {
  private api = inject(DashboardApiService);

  readonly stats = signal<DashboardStats | null>(null);
  readonly recentQuotes = signal<any[]>([]);
  readonly isLoading = signal(false);

  load() {
    this.isLoading.set(true);
    forkJoin({
      stats: this.api.getStats(),
      recent: this.api.getRecent(),
    }).subscribe({
      next: (data) => {
        this.stats.set(data.stats);
        this.recentQuotes.set(data.recent);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }
}
