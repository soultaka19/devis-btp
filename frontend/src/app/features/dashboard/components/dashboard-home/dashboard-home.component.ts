import { Component, computed, inject, OnInit } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { CurrencyPipe, DatePipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';
import { DashboardStore } from '../../state/dashboard.store';
import { AuthStore } from '../../../auth/state/auth.store';
import { LanguageService } from '../../../../core/i18n/language.service';

@Component({
  selector: 'app-dashboard-home',
  standalone: true,
  imports: [RouterLink, MatCardModule, MatButtonModule, MatIconModule, MatProgressBarModule, CurrencyPipe, DatePipe, TranslateModule],
  template: `
    <div class="dashboard">
      @if (store.isLoading()) {
        <mat-progress-bar mode="indeterminate" class="top-loader"></mat-progress-bar>
      }

      <div class="header">
        <div class="greeting">
          <h2>{{ 'DASHBOARD.GREETING' | translate:{name: authStore.user()?.full_name || ('NAV.USER' | translate)} }}</h2>
          <p class="date-label">{{ today | date:'EEEE d MMMM yyyy':'':dateLocale() }}</p>
        </div>
        <button mat-raised-button class="btn-accent" routerLink="/quote/new">
          <mat-icon>add</mat-icon> {{ 'DASHBOARD.NEW_QUOTE' | translate }}
        </button>
      </div>

      @if (store.stats(); as stats) {
        <div class="stats-grid">
          <div class="stat-card blue">
            <div class="stat-icon-wrap">
              <mat-icon>description</mat-icon>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.total_quotes }}</span>
              <span class="stat-label">{{ 'DASHBOARD.STAT_TOTAL' | translate }}</span>
            </div>
          </div>
          <div class="stat-card amber">
            <div class="stat-icon-wrap">
              <mat-icon>calendar_month</mat-icon>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.quotes_this_month }}</span>
              <span class="stat-label">{{ 'DASHBOARD.STAT_MONTH' | translate }}</span>
            </div>
          </div>
          <div class="stat-card green">
            <div class="stat-icon-wrap">
              <mat-icon>euro</mat-icon>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.avg_quote_value | currency:'EUR':'symbol':'1.0-0' }}</span>
              <span class="stat-label">{{ 'DASHBOARD.STAT_AVG' | translate }}</span>
            </div>
          </div>
          <div class="stat-card orange">
            <div class="stat-icon-wrap">
              <mat-icon>check_circle</mat-icon>
            </div>
            <div class="stat-content">
              <span class="stat-value">{{ stats.status_breakdown['accepted'] || 0 }}</span>
              <span class="stat-label">{{ 'DASHBOARD.STAT_ACCEPTED' | translate }}</span>
            </div>
          </div>
        </div>
      }

      <div class="section-header">
        <h3>{{ 'DASHBOARD.RECENT_QUOTES' | translate }}</h3>
      </div>

      @for (quote of store.recentQuotes(); track quote.id) {
        <div class="quote-row-card" [routerLink]="['/quote', quote.id]">
          <span class="ref">{{ quote.reference }}</span>
          <span class="client">{{ quote.client_name || ('DASHBOARD.NO_CLIENT' | translate) }}</span>
          <span class="title-col">{{ quote.title || ('DASHBOARD.NO_TITLE' | translate) }}</span>
          <span class="status-badge" [class]="quote.status">{{ quote.status }}</span>
          <span class="amount">{{ quote.total_ttc | currency:'EUR' }}</span>
          <mat-icon class="arrow-icon">chevron_right</mat-icon>
        </div>
      } @empty {
        <div class="empty-state">
          <mat-icon class="empty-icon">description</mat-icon>
          <p>{{ 'DASHBOARD.EMPTY' | translate }}</p>
          <button mat-raised-button class="btn-accent" routerLink="/quote/new">
            <mat-icon>add</mat-icon> {{ 'DASHBOARD.CREATE_FIRST' | translate }}
          </button>
        </div>
      }
    </div>
  `,
  styles: [`
    .dashboard { max-width: 100%; margin: 0 auto; }

    .top-loader {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 999;
    }

    /* Header */
    .header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 32px;
    }

    .greeting h2 {
      margin: 0 0 4px;
      font-size: 24px;
      font-weight: 700;
    }

    .date-label {
      color: var(--text-secondary);
      font-size: 14px;
      margin: 0;
      text-transform: capitalize;
    }

    /* Stat Cards */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 20px;
      margin-bottom: 40px;
    }

    .stat-card {
      background: white;
      border-radius: var(--radius-md);
      padding: 20px 24px;
      display: flex;
      align-items: center;
      gap: 16px;
      border: 1px solid var(--border);
      border-left: 4px solid;
      box-shadow: var(--shadow-sm);
      transition: box-shadow 0.2s ease, transform 0.2s ease;

      &:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
      }

      &.blue { border-left-color: var(--primary); }
      &.amber { border-left-color: var(--accent); }
      &.green { border-left-color: var(--success); }
      &.orange { border-left-color: var(--warning); }
    }

    .stat-icon-wrap {
      width: 48px;
      height: 48px;
      border-radius: var(--radius-sm);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;

      .blue & { background: rgba(27, 42, 74, 0.08); color: var(--primary); }
      .amber & { background: rgba(212, 146, 11, 0.1); color: var(--accent); }
      .green & { background: rgba(27, 122, 61, 0.08); color: var(--success); }
      .orange & { background: rgba(230, 126, 34, 0.1); color: var(--warning); }
    }

    .stat-content {
      display: flex;
      flex-direction: column;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: var(--text-primary);
      line-height: 1.2;
    }

    .stat-label {
      font-size: 13px;
      color: var(--text-secondary);
      margin-top: 2px;
    }

    /* Section Header */
    .section-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      h3 {
        margin: 0;
        font-size: 18px;
        font-weight: 600;
      }
    }

    /* Quote Rows */
    .quote-row-card {
      display: flex;
      align-items: center;
      gap: 16px;
      padding: 16px 20px;
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.2s ease;

      &:hover {
        border-color: var(--primary-light);
        box-shadow: var(--shadow-sm);
        background: #FAFBFF;
      }
    }

    .ref {
      font-weight: 600;
      color: var(--primary);
      min-width: 140px;
      font-size: 13px;
    }

    .client {
      min-width: 140px;
      color: var(--text-primary);
    }

    .title-col {
      flex: 1;
      color: var(--text-secondary);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .amount {
      font-weight: 600;
      color: var(--text-primary);
      min-width: 100px;
      text-align: right;
    }

    .arrow-icon {
      color: var(--text-secondary);
      font-size: 20px;
    }

    /* Empty State */
    .empty-state {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 64px 24px;
      background: white;
      border: 2px dashed var(--border);
      border-radius: var(--radius-md);
      text-align: center;
    }

    .empty-icon {
      font-size: 56px !important;
      width: 56px !important;
      height: 56px !important;
      color: var(--border) !important;
      margin-bottom: 16px;
    }

    .empty-state p {
      color: var(--text-secondary);
      margin: 0 0 20px;
      font-size: 16px;
    }

    @media (max-width: 768px) {
      .header { flex-direction: column; gap: 16px; }
      .quote-row-card { flex-wrap: wrap; gap: 8px; }
      .ref { min-width: auto; }
      .client { min-width: auto; }
      .title-col { display: none; }
    }
  `],
})
export class DashboardHomeComponent implements OnInit {
  store = inject(DashboardStore);
  authStore = inject(AuthStore);
  private langService = inject(LanguageService);
  today = new Date();

  dateLocale = computed(() => this.langService.isFrench() ? 'fr-FR' : 'en-US');

  ngOnInit() { this.store.load(); }
}
