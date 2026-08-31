import { Component, inject, signal } from '@angular/core';
import { Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { AuthStore } from '../auth/state/auth.store';
import { DemoStore } from '../../core/demo/demo.store';

/**
 * Entry point of the disposable demo.
 *
 * Nothing is asked of the visitor - no email address, no password. The page
 * states what the sandbox contains and what it costs (a bounded number of AI
 * attempts) *before* creating it, so the click is informed.
 */
@Component({
  selector: 'app-demo-entry',
  standalone: true,
  imports: [RouterLink, MatButtonModule, MatIconModule, MatProgressSpinnerModule, TranslateModule],
  template: `
    <div class="demo-page">
      <div class="demo-card">
        <mat-icon class="demo-logo">construction</mat-icon>
        <h1>{{ 'DEMO.TITLE' | translate }}</h1>
        <p class="demo-subtitle">{{ 'DEMO.SUBTITLE' | translate }}</p>

        <ul class="demo-points">
          <li>
            <mat-icon>lock_open</mat-icon>
            <span>{{ 'DEMO.POINT_NO_ACCOUNT' | translate }}</span>
          </li>
          <li>
            <mat-icon>description</mat-icon>
            <span>{{ 'DEMO.POINT_SEEDED' | translate }}</span>
          </li>
          <li>
            <mat-icon>auto_fix_high</mat-icon>
            <span>{{ 'DEMO.POINT_AI' | translate: { total: aiCalls } }}</span>
          </li>
          <li>
            <mat-icon>auto_delete</mat-icon>
            <span>{{ 'DEMO.POINT_ERASED' | translate }}</span>
          </li>
        </ul>

        @if (error()) {
          <div class="demo-error" [class.wait]="retryable()">
            <mat-icon>{{ retryable() ? 'hourglass_top' : 'error_outline' }}</mat-icon>
            <span>{{ error() }}</span>
          </div>
        }

        @if (loading()) {
          <div class="demo-loading">
            <mat-spinner diameter="28"></mat-spinner>
            <span>{{ 'DEMO.PREPARING' | translate }}</span>
          </div>
        } @else {
          <button mat-flat-button color="primary" class="demo-start" (click)="start()">
            <mat-icon>play_arrow</mat-icon>
            {{ (error() ? 'DEMO.RETRY' : 'DEMO.START') | translate }}
          </button>
        }

        <a class="demo-login" routerLink="/auth/login">{{ 'DEMO.LOGIN_LINK' | translate }}</a>
      </div>
    </div>
  `,
  styles: [`
    .demo-page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px 16px;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
    }

    .demo-card {
      width: 100%;
      max-width: 480px;
      background: var(--surface-alt);
      border-radius: 16px;
      padding: 32px 28px;
      box-shadow: 0 20px 48px rgba(0, 0, 0, 0.28);
      text-align: center;
    }

    .demo-logo {
      font-size: 40px;
      width: 40px;
      height: 40px;
      color: var(--accent);
    }

    h1 { margin: 8px 0 4px; font-size: 24px; }

    .demo-subtitle {
      margin: 0 0 20px;
      color: var(--text-secondary);
    }

    .demo-points {
      list-style: none;
      margin: 0 0 20px;
      padding: 0;
      text-align: left;

      li {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 7px 0;
        line-height: 1.5;
      }

      mat-icon {
        flex: none;
        font-size: 20px;
        width: 20px;
        height: 20px;
        color: var(--primary-light);
      }
    }

    .demo-error {
      display: flex;
      align-items: flex-start;
      gap: 8px;
      text-align: left;
      margin-bottom: 16px;
      padding: 10px 12px;
      border-radius: 8px;
      background: rgba(230, 126, 34, 0.12);
      color: var(--warning);

      &:not(.wait) {
        background: rgba(211, 47, 47, 0.1);
        color: #C62828;
      }

      mat-icon { flex: none; font-size: 20px; width: 20px; height: 20px; }
    }

    .demo-loading {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      padding: 8px 0 4px;
      color: var(--text-secondary);
    }

    .demo-start { width: 100%; }

    .demo-login {
      display: inline-block;
      margin-top: 16px;
      font-size: 13px;
      color: var(--text-secondary);
    }
  `],
})
export class DemoEntryComponent {
  private demo = inject(DemoStore);
  private auth = inject(AuthStore);
  private router = inject(Router);
  private translate = inject(TranslateService);

  /** Mirrors DEMO_AI_CALLS server-side; the real count comes back with the session. */
  readonly aiCalls = 5;

  readonly loading = signal(false);
  readonly error = signal<string | null>(null);
  /** A ceiling or a rate limit is a "come back in a minute", not a failure. */
  readonly retryable = signal(false);

  start(): void {
    this.loading.set(true);
    this.error.set(null);

    this.demo.create().subscribe({
      next: (session) => {
        this.auth.applySession(session.access_token);
        this.router.navigate(['/dashboard']);
      },
      error: (err) => {
        this.loading.set(false);
        this.retryable.set(err.status === 429 || err.status === 503);
        // The backend already localises its message through Accept-Language.
        this.error.set(err.error?.detail || this.translate.instant('DEMO.ERROR_GENERIC'));
      },
    });
  }
}
