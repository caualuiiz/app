"""Pydantic models used by the API layer."""
from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BusinessType = Literal[
    "BARBERSHOP", "BEAUTY_SALON", "MANICURE", "AESTHETICS", "PET_SHOP"
]
Role = Literal["OWNER", "MANAGER", "PROFESSIONAL"]
Status = Literal["ACTIVE", "INACTIVE", "PENDING"]


# ---------- Auth ----------
class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    password_confirm: str = Field(min_length=8, max_length=128)

    @field_validator("password_confirm")
    @classmethod
    def _match(cls, v: str, info):
        if info.data.get("password") and v != info.data["password"]:
            raise ValueError("As senhas não coincidem")
        return v


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ForgotPasswordIn(BaseModel):
    email: EmailStr


class ResetPasswordIn(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


# ---------- User ----------
class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: EmailStr
    status: Status
    created_at: str
    updated_at: str


# ---------- Company ----------
class CompanyCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    business_type: BusinessType


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    business_type: Optional[BusinessType] = None
    logo_url: Optional[str] = None
    establishment_photo_url: Optional[str] = None
    description: Optional[str] = Field(default=None, max_length=1000)
    phone: Optional[str] = Field(default=None, max_length=40)
    email: Optional[EmailStr] = None
    address: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=80)
    state: Optional[str] = Field(default=None, max_length=80)
    zip_code: Optional[str] = Field(default=None, max_length=20)


class CompanyOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    slug: str
    business_type: BusinessType
    logo_url: Optional[str] = None
    establishment_photo_url: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    status: Status
    created_at: str
    updated_at: str


# ---------- Membership ----------
class MembershipCreate(BaseModel):
    email: EmailStr
    role: Role = "PROFESSIONAL"
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)


class MembershipUpdate(BaseModel):
    role: Optional[Role] = None
    status: Optional[Status] = None


class MembershipOut(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    user_id: str
    company_id: str
    role: Role
    status: Status
    user_name: str
    user_email: str
    created_at: str
    updated_at: str


# ---------- Auth response ----------
class AuthResponse(BaseModel):
    user: UserOut
    active_company: Optional[CompanyOut] = None
    active_role: Optional[Role] = None
    needs_onboarding: bool = False
