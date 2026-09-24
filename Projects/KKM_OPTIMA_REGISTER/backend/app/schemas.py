from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

Status = Literal["NEW","IN_PROGRESS","WAITING_CLIENT","PROCESSING","COMPLETED","REJECTED"]

class ApplicationCreate(BaseModel):
    login: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1, max_length=255)
    inn: str
    company: str = Field(min_length=1, max_length=255)
    legal_address: str = Field(min_length=3)
    director: str = Field(min_length=1, max_length=255)
    director_inn: str
    director_phone: str
    director_email: EmailStr
    extra_phone: str
    extra_name: str | None = None
    object_type: str = Field(min_length=1)
    activity: str = Field(min_length=1)
    ugns: str = Field(min_length=1)
    place_type: str = Field(min_length=1)
    point_name: str = Field(min_length=1, max_length=255)
    point_address: str = Field(min_length=3)
    tax_regime: str = Field(min_length=1)
    vat: bool = False
    calc_types: list[str] = Field(min_length=1)
    comment: str | None = None

    @field_validator("inn", "director_inn")
    @classmethod
    def valid_inn(cls, v):
        if not v.isdigit() or len(v) != 14:
            raise ValueError("ИНН должен состоять из 14 цифр")
        return v

    @field_validator("director_phone", "extra_phone")
    @classmethod
    def valid_phone(cls, v):
        if not v.startswith("+996 ") or len(v.replace(" ", "")) != 13:
            raise ValueError("Неверный формат телефона")
        return v

class DocumentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    document_type: str
    original_name: str
    mime_type: str
    size_bytes: int
    sha256: str
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
    password_available: bool = False
    public_token: str | None = None
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

class AssignManager(BaseModel):
    manager_id: str

class ManagerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    username: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PublicStatus(BaseModel):
    application_number: str
    status: str
    company: str
    created_at: datetime
