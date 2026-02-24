import { Injectable, computed, inject, signal } from '@angular/core';
import { TranslateService } from '@ngx-translate/core';

const STORAGE_KEY = 'btp_language';

@Injectable({ providedIn: 'root' })
export class LanguageService {
  private translate = inject(TranslateService);

  readonly currentLang = signal<'fr' | 'en'>(this.loadLang());

  readonly isFrench = computed(() => this.currentLang() === 'fr');

  constructor() {
    this.translate.setDefaultLang('fr');
    this.translate.use(this.currentLang());
  }

  toggleLanguage(): void {
    const next = this.currentLang() === 'fr' ? 'en' : 'fr';
    this.currentLang.set(next);
    this.translate.use(next);
    localStorage.setItem(STORAGE_KEY, next);
  }

  instant(key: string, params?: Record<string, unknown>): string {
    return this.translate.instant(key, params);
  }

  private loadLang(): 'fr' | 'en' {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'en' || stored === 'fr') return stored;
    }
    return 'fr';
  }
}
