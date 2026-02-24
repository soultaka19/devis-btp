import { Component, inject, OnInit } from '@angular/core';
import { MatTabsModule } from '@angular/material/tabs';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { CompanyStore } from '../../state/company.store';
import { CompanyInfoFormComponent } from './company-info-form/company-info-form.component';
import { BankingFormComponent } from './banking-form/banking-form.component';
import { InsuranceFormComponent } from './insurance-form/insurance-form.component';
import { TermsFormComponent } from './terms-form/terms-form.component';
import { LogoUploadComponent } from './logo-upload/logo-upload.component';

@Component({
  selector: 'app-company-settings',
  standalone: true,
  imports: [
    MatTabsModule,
    MatProgressBarModule,
    MatIconModule,
    TranslateModule,
    CompanyInfoFormComponent,
    BankingFormComponent,
    InsuranceFormComponent,
    TermsFormComponent,
    LogoUploadComponent,
  ],
  template: `
    <div class="settings-page">
      <div class="page-header">
        <mat-icon class="page-icon">business</mat-icon>
        <div>
          <h2>{{ 'COMPANY.TITLE' | translate }}</h2>
          <p class="page-subtitle">{{ 'COMPANY.SUBTITLE' | translate }}</p>
        </div>
      </div>

      @if (store.loading()) {
        <mat-progress-bar mode="indeterminate"></mat-progress-bar>
      }
      @if (store.error()) {
        <div class="error-banner">
          <mat-icon>error_outline</mat-icon>
          <span>{{ store.error() }}</span>
        </div>
      }

      <mat-tab-group class="settings-tabs" animationDuration="200ms">
        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon>info</mat-icon>
            <span>{{ 'COMPANY.TAB_INFO' | translate }}</span>
          </ng-template>
          <div class="tab-content">
            <div class="settings-card">
              <app-company-info-form [data]="store.companyInfo()" (save)="store.saveInfo($event)" [saving]="store.saving()" />
            </div>
            <div class="settings-card">
              <app-logo-upload [logoPath]="store.companyInfo()?.logo_path" (upload)="store.uploadLogo($event)" />
            </div>
          </div>
        </mat-tab>
        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon>account_balance</mat-icon>
            <span>{{ 'COMPANY.TAB_BANKING' | translate }}</span>
          </ng-template>
          <div class="tab-content">
            <div class="settings-card">
              <app-banking-form [data]="store.banking()" (save)="store.saveBanking($event)" [saving]="store.saving()" />
            </div>
          </div>
        </mat-tab>
        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon>shield</mat-icon>
            <span>{{ 'COMPANY.TAB_INSURANCE' | translate }}</span>
          </ng-template>
          <div class="tab-content">
            <div class="settings-card">
              <app-insurance-form [data]="store.insurance()" (save)="store.saveInsurance($event)" [saving]="store.saving()" />
            </div>
          </div>
        </mat-tab>
        <mat-tab>
          <ng-template mat-tab-label>
            <mat-icon>gavel</mat-icon>
            <span>{{ 'COMPANY.TAB_TERMS' | translate }}</span>
          </ng-template>
          <div class="tab-content">
            <div class="settings-card">
              <app-terms-form [data]="store.terms()" (save)="store.saveTerms($event)" [saving]="store.saving()" />
            </div>
          </div>
        </mat-tab>
      </mat-tab-group>
    </div>
  `,
  styles: [`
    .settings-page {
      max-width: 100%;
      margin: 0 auto;
    }

    .page-header {
      display: flex;
      align-items: center;
      gap: 16px;
      margin-bottom: 28px;

      h2 {
        margin: 0 0 4px;
        font-size: 22px;
        font-weight: 700;
      }
    }

    .page-icon {
      font-size: 36px !important;
      width: 36px !important;
      height: 36px !important;
      color: var(--primary) !important;
    }

    .page-subtitle {
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

    .settings-tabs {
      .mat-mdc-tab {
        min-width: 140px;

        mat-icon {
          margin-right: 8px;
          font-size: 20px;
        }
      }
    }

    .tab-content {
      padding: 28px 0;
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .settings-card {
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 28px;
    }
  `],
})
export class CompanySettingsComponent implements OnInit {
  store = inject(CompanyStore);
  ngOnInit() { this.store.loadAll(); }
}
