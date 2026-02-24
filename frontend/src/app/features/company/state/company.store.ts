import { Injectable, computed, inject, signal } from '@angular/core';
import { CompanyInfo, BankingInfo, InsuranceInfo, TermsInfo } from '../models/company.model';
import { CompanyApiService } from '../services/company-api.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { forkJoin } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class CompanyStore {
  private api = inject(CompanyApiService);
  private lang = inject(LanguageService);

  readonly companyInfo = signal<CompanyInfo | null>(null);
  readonly banking = signal<BankingInfo | null>(null);
  readonly insurance = signal<InsuranceInfo | null>(null);
  readonly terms = signal<TermsInfo | null>(null);
  readonly loading = signal(false);
  readonly saving = signal(false);
  readonly error = signal<string | null>(null);

  readonly isComplete = computed(() =>
    !!this.companyInfo() && !!this.banking() && !!this.insurance() && !!this.terms()
  );

  loadAll() {
    this.loading.set(true);
    forkJoin({
      info: this.api.getInfo(),
      banking: this.api.getBanking(),
      insurance: this.api.getInsurance(),
      terms: this.api.getTerms(),
    }).subscribe({
      next: (data) => {
        this.companyInfo.set(data.info);
        this.banking.set(data.banking);
        this.insurance.set(data.insurance);
        this.terms.set(data.terms);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_LOAD'));
        this.loading.set(false);
      },
    });
  }

  saveInfo(data: CompanyInfo) {
    this.saving.set(true);
    this.api.saveInfo(data).subscribe({
      next: (res) => { this.companyInfo.set(res); this.saving.set(false); },
      error: (err) => { this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_SAVE')); this.saving.set(false); },
    });
  }

  saveBanking(data: BankingInfo) {
    this.saving.set(true);
    this.api.saveBanking(data).subscribe({
      next: (res) => { this.banking.set(res); this.saving.set(false); },
      error: (err) => { this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_SAVE')); this.saving.set(false); },
    });
  }

  saveInsurance(data: InsuranceInfo) {
    this.saving.set(true);
    this.api.saveInsurance(data).subscribe({
      next: (res) => { this.insurance.set(res); this.saving.set(false); },
      error: (err) => { this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_SAVE')); this.saving.set(false); },
    });
  }

  saveTerms(data: TermsInfo) {
    this.saving.set(true);
    this.api.saveTerms(data).subscribe({
      next: (res) => { this.terms.set(res); this.saving.set(false); },
      error: (err) => { this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_SAVE')); this.saving.set(false); },
    });
  }

  uploadLogo(file: File) {
    this.saving.set(true);
    this.api.uploadLogo(file).subscribe({
      next: (res) => { this.companyInfo.set(res); this.saving.set(false); },
      error: (err) => { this.error.set(err.error?.detail || this.lang.instant('COMPANY.ERROR_UPLOAD')); this.saving.set(false); },
    });
  }
}
