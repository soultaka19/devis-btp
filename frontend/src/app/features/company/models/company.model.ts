export interface CompanyInfo {
  id?: number;
  name: string;
  siret: string;
  address: string;
  city: string;
  postal_code: string;
  phone: string;
  email: string;
  logo_path?: string;
}

export interface BankingInfo {
  id?: number;
  bank_name: string;
  iban: string;
  bic: string;
}

export interface InsuranceInfo {
  id?: number;
  provider: string;
  policy_number: string;
  coverage_zone: string;
}

export interface TermsInfo {
  id?: number;
  payment_terms: string;
  validity_days: number;
  late_penalty_rate: number;
  general_conditions: string;
}
