import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { TranslateModule } from '@ngx-translate/core';
import { AuthStore } from '../../features/auth/state/auth.store';
import { DemoStore } from './demo.store';

/**
 * Permanent strip shown while a sandbox is open.
 *
 * It answers, without the visitor having to ask: how long this space lives,
 * how many AI attempts remain, and that nothing here is real data.
 */
@Component({
  selector: 'app-demo-banner',
  standalone: true,
  imports: [MatButtonModule, MatIconModule, MatTooltipModule, TranslateModule],
  template: `
    <div class="demo-banner" [class.expired]="demo.expired()">
      <mat-icon class="banner-icon">science</mat-icon>
      <span class="banner-label">{{ 'DEMO.BANNER_LABEL' | translate }}</span>

      @if (demo.expired()) {
        <span class="banner-item">{{ 'DEMO.BANNER_EXPIRED' | translate }}</span>
      } @else {
        <span class="banner-item">
          <mat-icon>schedule</mat-icon>
          {{ 'DEMO.BANNER_TIME' | translate: { time: demo.timeLeft() } }}
        </span>
        <span class="banner-item" [class.exhausted]="demo.aiCallsRemaining() === 0">
          <mat-icon>auto_fix_high</mat-icon>
          {{ 'DEMO.BANNER_AI' | translate: {
               remaining: demo.aiCallsRemaining(), total: demo.aiCallsTotal() } }}
        </span>
      }

      <span class="banner-hint">{{ 'DEMO.BANNER_HINT' | translate }}</span>
      <span class="spacer"></span>

      @if (demo.expired()) {
        <button mat-flat-button class="banner-action" (click)="restart()">
          {{ 'DEMO.RESTART' | translate }}
        </button>
      } @else {
        <button mat-button class="banner-action"
                [matTooltip]="'DEMO.LEAVE_HINT' | translate" (click)="leave()">
          {{ 'DEMO.LEAVE' | translate }}
        </button>
      }
    </div>
  `,
  styles: [`
    .demo-banner {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 6px 14px;
      padding: 6px 16px;
      background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 100%);
      color: #1A1A2E;
      font-size: 13px;
      font-weight: 500;
      z-index: 1100;

      &.expired {
        background: var(--warning);
        color: #fff;
      }
    }

    .banner-icon { font-size: 18px; width: 18px; height: 18px; }

    .banner-label {
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .banner-item {
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-variant-numeric: tabular-nums;

      mat-icon { font-size: 16px; width: 16px; height: 16px; }

      &.exhausted { opacity: 0.75; text-decoration: line-through; }
    }

    .banner-hint { opacity: 0.8; }

    .spacer { flex: 1 1 auto; }

    .banner-action { font-size: 13px; }

    @media (max-width: 767px) {
      .demo-banner { font-size: 12px; padding: 6px 10px; }
      .banner-hint { display: none; }
    }
  `],
})
export class DemoBannerComponent {
  demo = inject(DemoStore);
  private auth = inject(AuthStore);
  private router = inject(Router);

  /** Leaving drops the token; the sandbox itself is purged server-side at expiry. */
  leave(): void {
    this.demo.clear();
    this.auth.logout();
  }

  restart(): void {
    this.demo.clear();
    this.auth.clearSession();
    this.router.navigate(['/demo']);
  }
}
