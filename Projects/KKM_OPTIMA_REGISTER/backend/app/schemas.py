from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


Status = Literal[
    "NEW",
    "IN_PROGRESS",
    "WAITING_CLIENT",
    "PROCESSING",
    "COMPLETED",
    "REJECTED",
]


class ApplicationCreate(BaseModel):
    login: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)

    inn: str
    company: str
    legal_address: str
    director: str
    director_inn: str
    director_phone: str
    director_email: EmailStr

    extra_phone: str
    extra_name: str | None = None

    object_type: str
    activity: str
    ugns: str

    place_type: str
    point_name: str
    point_address: str

    tax_regime: str
    vat: bool = False
    calc_types: list[str] = Field(min_length=1)
    comment: str | None = None

    @field_validator("inn", "director_inn")
    @classmethod
    def validate_inn(cls, value: str) -> str:
        if not value.isdigit() or len(value) != 14:
            raise ValueError("ИНН должен состоять из 14 цифр")
        return value

    @field_validator("director_phone", "extra_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not value.startswith("+996 ") or len(value.replace(" ", "")) != 13:
            raise ValueError("Неверный формат телефона")
        return value


class DocumentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_type: str
    original_name: str
    mime_type: str
    size_bytes: int
    created_at: datetime


class ApplicationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    application_number: str
    status: str
    inn: str
    company: str
    point_name: str
    ugns: str
    manager_id: str | None
    created_at: datetime


class ApplicationDetails(ApplicationListItem):
    login: str
    password_available: bool

    legal_address: str
    director: str
    director_inn: str
    director_phone: str
    director_email: EmailStr

    extra_phone: str
    extra_name: str | None

    object_type: str
    activity: str

    place_type: str
    point_address: str

    tax_regime: str
    vat: bool
    calc_types: list[str]
    comment: str | None

    documents: list[DocumentInfo]


class StatusUpdate(BaseModel):
    status: Status
    comment: str | None = None


class ManagerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    username: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
