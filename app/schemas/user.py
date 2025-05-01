from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber

from app.database.models import UserType
from app.database.types import ProviderType, DocumentType, DocumentStatus


class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    surname: str
    patronymic: str | None = Field(default=None, min_length=3, max_length=30)


class UserCreate(UserBase):
    password_hash: str = Field(min_length=8)


class OwnerCreate(UserCreate):
    phone: PhoneNumber
    address: str | None = Field(default=None, min_length=3, max_length=150)
    role: UserType = Field(default=UserType.owner.value)


class ProviderCreate(UserCreate):
    company_name: str = Field(min_length=3, max_length=150)
    provider_type: ProviderType
    service_radius_km: int = Field(
        default=10,
    )
    hourly_rate: float
    role: UserType = Field(default=UserType.provider.value)


class UserAuth(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    id: int
    role: UserType

    class Config:
        from_attributes = True


class OwnerOut(UserOut):
    phone: PhoneNumber
    address: str | None = Field(default=None, min_length=3, max_length=150)


class ProviderOut(UserOut):
    id: int
    company_name: str = Field(min_length=3, max_length=150)
    provider_type: ProviderType
    service_radius_km: int = Field(
        default=10,
    )
    hourly_rate: float


class ProviderDoc(BaseModel):
    document_type: DocumentType
    file_url: str
    status: DocumentStatus


class Token(BaseModel):
    access_token: str
    token_type: str
    role: Optional[str] = None


class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[UserType] = None
