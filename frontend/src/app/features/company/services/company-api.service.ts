import { Injectable, inject } from '@angular/core';
import { ApiService } from '../../../core/api/api.service';
import { CompanyInfo, BankingInfo, InsuranceInfo, TermsInfo } from '../models/company.model';

@Injectable({ providedIn: 'root' })
export class CompanyApiService {
  private api = inject(ApiService);

  getInfo() { return this.api.get<CompanyInfo | null>('/company/info'); }
  saveInfo(data: CompanyInfo) { return this.api.put<CompanyInfo>('/company/info', data); }

  getBanking() { return this.api.get<BankingInfo | null>('/company/banking'); }
  saveBanking(data: BankingInfo) { return this.api.put<BankingInfo>('/company/banking', data); }

  getInsurance() { return this.api.get<InsuranceInfo | null>('/company/insurance'); }
  saveInsurance(data: InsuranceInfo) { return this.api.put<InsuranceInfo>('/company/insurance', data); }

  getTerms() { return this.api.get<TermsInfo | null>('/company/terms'); }
  saveTerms(data: TermsInfo) { return this.api.put<TermsInfo>('/company/terms', data); }

  uploadLogo(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    return this.api.upload<CompanyInfo>('/company/logo', formData);
  }
}
