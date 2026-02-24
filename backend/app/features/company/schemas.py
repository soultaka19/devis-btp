from pydantic import BaseModel, field_validator


class CompanyCreate(BaseModel):
    name: str
    siret: str
    address: str
    city: str
    postal_code: str
    phone: str
    email: str

    @field_validator("siret")
    @classmethod
    def validate_siret(cls, v: str) -> str:
        digits = v.replace(" ", "")
        if not digits.isdigit() or len(digits) != 14:
            raise ValueError("Le SIRET doit contenir exactement 14 chiffres")
        return digits


class CompanyResponse(CompanyCreate):
    id: int
    logo_path: str | None = None
    model_config = {"from_attributes": True}


class BankingCreate(BaseModel):
    bank_name: str
    iban: str
    bic: str

    @field_validator("iban")
    @classmethod
    def validate_iban(cls, v: str) -> str:
        clean = v.replace(" ", "").upper()
        if len(clean) < 15 or len(clean) > 34:
            raise ValueError("IBAN invalide")
        return clean


class BankingResponse(BankingCreate):
    id: int
    model_config = {"from_attributes": True}


class InsuranceCreate(BaseModel):
    provider: str
    policy_number: str
    coverage_zone: str


class InsuranceResponse(InsuranceCreate):
    id: int
    model_config = {"from_attributes": True}


class TermsCreate(BaseModel):
    payment_terms: str = "Paiement à 30 jours"
    validity_days: int = 30
    late_penalty_rate: float = 3.0
    general_conditions: str = ""


class TermsResponse(TermsCreate):
    id: int
    model_config = {"from_attributes": True}
