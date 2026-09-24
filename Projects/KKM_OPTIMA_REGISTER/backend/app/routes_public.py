import secrets

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import select, text
from sqlalchemy.orm import Session, selectinload
from fastapi import Form

from .auth import encrypt_secret
from .config import get_settings
from .db import get_db
from .models import Application, AuditLog, Document
from .schemas import ApplicationCreate, ApplicationDetails, PublicStatus
from .services import (
    application_number,
    load_upload,
    public_token_hash,
    remove_stored_files,
    store_upload,
    validate_file,
)

router = APIRouter(prefix="/api")
s = get_settings()


@router.post("/applications", response_model=ApplicationDetails, status_code=201)
async def create_application(
    data: str = Form(...),
    registration_document: UploadFile = File(...),
    passport_front: UploadFile = File(...),
    passport_back: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        payload = ApplicationCreate.model_validate_json(data)
    except Exception as exc:
        raise HTTPException(422, "Некорректные данные заявки") from exc

    if payload.ugns == "other":
        if not payload.ugns_other:
            raise HTTPException(422, "Для другого УГНС укажите район вручную")
    elif payload.ugns_other:
        raise HTTPException(422, "ugns_other допустим только для значения other")

    loaded: list[tuple[str, UploadFile, bytes]] = []
    limit = s.max_file_size_mb * 1024 * 1024

    for doc_type, upload in [
        ("REGISTRATION", registration_document),
        ("PASSPORT_FRONT", passport_front),
        ("PASSPORT_BACK", passport_back),
    ]:
        content = load_upload(upload)
        if len(content) > limit:
            raise HTTPException(413, f"Файл {upload.filename or ''} слишком большой")
        validate_file(content, upload.content_type or "")
        loaded.append((doc_type, upload, content))

    token = secrets.token_urlsafe(32)
    stored_names: list[str] = []

    try:
        item = Application(
            application_number=application_number(),
            public_token_hash=public_token_hash(token),
            login=payload.login,
            lk_password_encrypted=encrypt_secret(payload.password),
            **payload.model_dump(exclude={"login", "password"}),
        )
        db.add(item)
        db.flush()

        for doc_type, upload, content in loaded:
            storage_name, sha = store_upload(upload, content)
            stored_names.append(storage_name)
            db.add(
                Document(
                    application_id=item.id,
                    document_type=doc_type,
                    original_name=(upload.filename or "file")[:255],
                    storage_name=storage_name,
                    mime_type=upload.content_type or "application/octet-stream",
                    size_bytes=len(content),
                    sha256=sha,
                )
            )

        db.add(AuditLog(
            application_id=item.id,
            action="CREATED",
            details={
                "source": "public_form",
                "form_version": "original_html_v1",
                "documents": [x[0] for x in loaded],
            },
        ))
        db.commit()
    except Exception:
        db.rollback()
        remove_stored_files(stored_names)
        raise

    item = db.scalar(
        select(Application).options(selectinload(Application.documents)).where(Application.id == item.id)
    )
    if not item:
        raise HTTPException(500, "Заявка не создана")
    return ApplicationDetails.model_validate(item, from_attributes=True).model_copy(update={"public_token": token})


@router.get("/public/{token}", response_model=PublicStatus)
def public_status(token: str, db: Session = Depends(get_db)):
    item = db.scalar(select(Application).where(Application.public_token_hash == public_token_hash(token)))
    if not item:
        raise HTTPException(404, "Заявка не найдена")
    return PublicStatus(
        application_number=item.application_number,
        status=item.status,
        company=item.company,
        created_at=item.created_at,
    )
