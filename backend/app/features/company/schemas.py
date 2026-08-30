from pydantic import BaseModel, Field, field_validator

# Length limits mirror the String(n) columns in models.py
# (a longer value made PostgreSQL fail with a 500)


class CompanyCreate(BaseModel):
    name: str = Field(max_length=255)
    siret: str
    address: str
    city: str = Field(max_length=255)
    postal_code: str = Field(max_length=10)
    phone: str = Field(max_length=20)
    email: str = Field(max_length=255)

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
    bank_name: str = Field(max_length=255)
    iban: str
    bic: str = Field(max_length=11)

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
    provider: str = Field(max_length=255)
    policy_number: str = Field(max_length=100)
    coverage_zone: str = Field(max_length=255)


class InsuranceResponse(InsuranceCreate):
    id: int
    model_config = {"from_attributes": True}


class TermsCreate(BaseModel):
    payment_terms: str = "Paiement à 30 jours"
    validity_days: int = Field(default=30, ge=0, le=3650)
    late_penalty_rate: float = Field(default=3.0, ge=0, le=100)
    general_conditions: str = ""


class TermsResponse(TermsCreate):
    id: int
    model_config = {"from_attributes": True}
