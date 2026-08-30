from pydantic import BaseModel, EmailStr, Field, field_validator

# bcrypt only hashes the first 72 bytes and bcrypt >= 5 raises on longer passwords (was a 500)
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_BYTES = 72


def _check_password_bytes(v: str) -> str:
    if len(v.encode("utf-8")) > PASSWORD_MAX_BYTES:
        raise ValueError(f"Le mot de passe ne doit pas dépasser {PASSWORD_MAX_BYTES} octets")
    return v


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_BYTES)
    full_name: str = Field(min_length=1, max_length=255)

    _password_bytes = field_validator("password")(_check_password_bytes)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(max_length=PASSWORD_MAX_BYTES)

    _password_bytes = field_validator("password")(_check_password_bytes)


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str

    model_config = {"from_attributes": True}
