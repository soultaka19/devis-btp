import { Component, computed, HostListener, inject, signal, ViewChild } from '@angular/core';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule, MatSidenav } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import { AuthStore } from './features/auth/state/auth.store';
import { LanguageService } from './core/i18n/language.service';

@Component({
  selector: 'app-root',
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatToolbarModule,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatListModule,
    MatTooltipModule,
    TranslateModule,
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  @ViewChild('sidenav') sidenav!: MatSidenav;

  authStore = inject(AuthStore);
  lang = inject(LanguageService);

  // Persisted preferences
  layoutMode = signal<'sidebar' | 'toolbar'>(this.loadLayoutMode());
  sidebarCollapsed = signal<boolean>(this.loadSidebarCollapsed());

  // Responsive
  isMobile = signal<boolean>(false);

  // Computed sidenav state
  sidenavOpened = computed(() => {
    if (this.isMobile()) return false;
    return this.layoutMode() === 'sidebar';
  });

  sidenavMode = computed<'side' | 'over'>(() => {
    if (this.isMobile()) return 'over';
    return 'side';
  });

  showToolbar = computed(() => {
    return this.isMobile() || this.layoutMode() === 'toolbar';
  });

  constructor() {
    this.checkMobile();
  }

  @HostListener('window:resize')
  onResize() {
    this.checkMobile();
  }

  private checkMobile() {
    if (typeof window !== 'undefined') {
      this.isMobile.set(window.innerWidth < 768);
    }
  }

  private loadLayoutMode(): 'sidebar' | 'toolbar' {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem('btp_layout_mode');
      if (stored === 'toolbar' || stored === 'sidebar') return stored;
    }
    return 'sidebar';
  }

  private loadSidebarCollapsed(): boolean {
    if (typeof localStorage !== 'undefined') {
      return localStorage.getItem('btp_sidebar_collapsed') === 'true';
    }
    return false;
  }

  toggleLayout() {
    const next = this.layoutMode() === 'sidebar' ? 'toolbar' : 'sidebar';
    this.layoutMode.set(next);
    localStorage.setItem('btp_layout_mode', next);
  }

  toggleSidebarCollapse() {
    const next = !this.sidebarCollapsed();
    this.sidebarCollapsed.set(next);
    localStorage.setItem('btp_sidebar_collapsed', String(next));
  }

  toggleMobileMenu() {
    this.sidenav?.toggle();
  }

  onNavClick() {
    if (this.isMobile()) {
      this.sidenav?.close();
    }
  }

  getUserInitials(): string {
    const name = this.authStore.user()?.full_name;
    if (!name) return 'U';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
  }
}
