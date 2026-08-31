import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { AuthStore } from '../../state/auth.store';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    RouterLink,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatProgressSpinnerModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="auth-page">
      <div class="auth-branding">
        <div class="branding-content">
          <mat-icon class="branding-icon">construction</mat-icon>
          <h1>Devis BTP</h1>
          <p class="branding-tagline">{{ 'AUTH.TAGLINE_LOGIN' | translate }}</p>
          <div class="branding-features">
            <div class="feature-item">
              <mat-icon>mic</mat-icon>
              <span>{{ 'AUTH.FEATURE_VOICE' | translate }}</span>
            </div>
            <div class="feature-item">
              <mat-icon>auto_fix_high</mat-icon>
              <span>{{ 'AUTH.FEATURE_AI' | translate }}</span>
            </div>
            <div class="feature-item">
              <mat-icon>description</mat-icon>
              <span>{{ 'AUTH.FEATURE_PDF' | translate }}</span>
            </div>
          </div>
        </div>
        <div class="branding-pattern"></div>
      </div>

      <div class="auth-form-side">
        <div class="auth-card">
          <div class="auth-card-header">
            <h2>{{ 'AUTH.LOGIN_TITLE' | translate }}</h2>
            <p class="auth-subtitle">{{ 'AUTH.LOGIN_SUBTITLE' | translate }}</p>
          </div>

          @if (authStore.error()) {
            <div class="error-banner">
              <mat-icon>error_outline</mat-icon>
              <span>{{ authStore.error() }}</span>
            </div>
          }

          <form [formGroup]="form" (ngSubmit)="onSubmit()">
            <mat-form-field class="full-width" appearance="outline">
              <mat-label>{{ 'AUTH.EMAIL' | translate }}</mat-label>
              <mat-icon matPrefix>email</mat-icon>
              <input matInput formControlName="email" type="email">
            </mat-form-field>
            <mat-form-field class="full-width" appearance="outline">
              <mat-label>{{ 'AUTH.PASSWORD' | translate }}</mat-label>
              <mat-icon matPrefix>lock</mat-icon>
              <input matInput formControlName="password" type="password">
            </mat-form-field>
            <button mat-raised-button class="btn-accent submit-btn full-width" type="submit"
                    [disabled]="form.invalid || authStore.loading()">
              @if (authStore.loading()) {
                <mat-spinner diameter="20"></mat-spinner>
              } @else {
                {{ 'AUTH.SUBMIT_LOGIN' | translate }}
              }
            </button>
          </form>

          <div class="auth-footer">
            <span>{{ 'AUTH.NO_ACCOUNT' | translate }}</span>
            <a routerLink="/auth/register">{{ 'AUTH.REGISTER_LINK' | translate }}</a>
          </div>

          <div class="auth-demo">
            <a routerLink="/demo">
              <mat-icon>play_circle</mat-icon>
              {{ 'AUTH.TRY_DEMO' | translate }}
            </a>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .auth-page {
      display: flex;
      min-height: 100vh;
    }

    /* Branding Left Panel */
    .auth-branding {
      flex: 1;
      background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      position: relative;
      overflow: hidden;
      padding: 48px;
    }

    .branding-content {
      position: relative;
      z-index: 2;
      color: white;
      max-width: 420px;
    }

    .branding-icon {
      font-size: 56px !important;
      width: 56px !important;
      height: 56px !important;
      color: var(--accent) !important;
      margin-bottom: 16px;
    }

    .branding-content h1 {
      color: white;
      font-size: 36px;
      font-weight: 700;
      margin: 0 0 12px;
    }

    .branding-tagline {
      font-size: 18px;
      opacity: 0.85;
      margin: 0 0 40px;
      line-height: 1.6;
    }

    .branding-features {
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .feature-item {
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 15px;
      opacity: 0.9;

      mat-icon {
        color: var(--accent-light);
        font-size: 22px;
        width: 22px;
        height: 22px;
      }
    }

    .branding-pattern {
      position: absolute;
      inset: 0;
      background-image:
        radial-gradient(circle at 20% 80%, rgba(212, 146, 11, 0.15) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.05) 0%, transparent 50%);
      z-index: 1;
    }

    /* Form Right Panel */
    .auth-form-side {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 48px;
      background: var(--surface);
    }

    .auth-card {
      width: 100%;
      max-width: 420px;
      background: white;
      border-radius: var(--radius-lg);
      padding: 40px;
      box-shadow: var(--shadow-lg);
    }

    .auth-card-header {
      margin-bottom: 32px;

      h2 {
        font-size: 24px;
        font-weight: 700;
        margin: 0 0 8px;
        color: var(--primary);
      }
    }

    .auth-subtitle {
      color: var(--text-secondary);
      margin: 0;
      font-size: 14px;
    }

    .error-banner {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 12px 16px;
      background: rgba(192, 57, 43, 0.08);
      border-radius: var(--radius-sm);
      color: var(--danger);
      font-size: 13px;
      margin-bottom: 20px;

      mat-icon { font-size: 18px; width: 18px; height: 18px; }
    }

    form {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .full-width { width: 100%; }

    .submit-btn {
      height: 48px;
      font-size: 15px;
      border-radius: var(--radius-sm) !important;
      margin-top: 8px;
    }

    .auth-demo {
      text-align: center;
      margin-top: 12px;

      a {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: var(--text-secondary);

        mat-icon { font-size: 18px; width: 18px; height: 18px; }

        &:hover { color: var(--accent); }
      }
    }

    .auth-footer {
      text-align: center;
      margin-top: 24px;
      font-size: 14px;
      color: var(--text-secondary);

      a {
        color: var(--accent);
        font-weight: 600;
        margin-left: 4px;

        &:hover { text-decoration: underline; }
      }
    }

    @media (max-width: 768px) {
      .auth-page { flex-direction: column; }
      .auth-branding {
        padding: 32px 24px;
        min-height: auto;
      }
      .branding-features { display: none; }
      .auth-form-side { padding: 24px; }
      .auth-card { padding: 24px; }
    }
  `],
})
export class LoginComponent {
  authStore = inject(AuthStore);
  private fb = inject(FormBuilder);

  form = this.fb.nonNullable.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', [Validators.required, Validators.minLength(6)]],
  });

  onSubmit() {
    if (this.form.valid) {
      const { email, password } = this.form.getRawValue();
      this.authStore.login(email, password);
    }
  }
}
