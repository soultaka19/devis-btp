import { Injectable, computed, inject, signal } from '@angular/core';
import { Router } from '@angular/router';
import { ApiService } from '../../../core/api/api.service';
import { LanguageService } from '../../../core/i18n/language.service';

interface User {
  id: number;
  email: string;
  full_name: string;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

@Injectable({ providedIn: 'root' })
export class AuthStore {
  private api = inject(ApiService);
  private router = inject(Router);
  private lang = inject(LanguageService);

  readonly user = signal<User | null>(null);
  readonly loading = signal(false);
  readonly error = signal<string | null>(null);

  readonly isAuthenticated = computed(() => !!this.user() || !!localStorage.getItem('access_token'));

  constructor() {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.loadUser();
    }
  }

  async login(email: string, password: string) {
    this.loading.set(true);
    this.error.set(null);
    this.api.post<TokenResponse>('/auth/login', { email, password }).subscribe({
      next: (res) => {
        localStorage.setItem('access_token', res.access_token);
        localStorage.setItem('refresh_token', res.refresh_token);
        this.loadUser();
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('AUTH.ERROR_LOGIN'));
        this.loading.set(false);
      },
    });
  }

  async register(email: string, password: string, fullName: string) {
    this.loading.set(true);
    this.error.set(null);
    this.api.post('/auth/register', { email, password, full_name: fullName }).subscribe({
      next: () => {
        this.login(email, password);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('AUTH.ERROR_REGISTER'));
        this.loading.set(false);
      },
    });
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.user.set(null);
    this.router.navigate(['/auth/login']);
  }

  private loadUser() {
    this.api.get<User>('/auth/me').subscribe({
      next: (user) => {
        this.user.set(user);
        this.loading.set(false);
      },
      error: () => {
        this.logout();
      },
    });
  }
}
