from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from .auth import encrypt_secret
from .config import get_settings
from .db import get_db
from .models import Application, AuditLog, Document
from .schemas import ApplicationCreate, ApplicationDetails, PublicStatus
from .services import application_number, load_upload, public_token_hash, store_upload, validate_file
import secrets

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
        p = ApplicationCreate.model_validate_json(data)
    except Exception as exc:
        raise HTTPException(422, f"Некорректные данные заявки: {exc}")

    loaded = []
    limit = s.max_file_size_mb * 1024 * 1024
    for typ, up in [
        ("REGISTRATION", registration_document),
        ("PASSPORT_FRONT", passport_front),
        ("PASSPORT_BACK", passport_back),
    ]:
        content = await load_upload(up)
        if len(content) > limit:
            raise HTTPException(413, "Файл слишком большой")
        validate_file(content, up.content_type or "")
        loaded.append((typ, up, content))

    token = secrets.token_urlsafe(24)
    item = Application(
        application_number=application_number(),
        public_token_hash=public_token_hash(token),
        login=p.login,
        lk_password_encrypted=encrypt_secret(p.password),
        **p.model_dump(exclude={"login", "password"}),
    )
    db.add(item)
    db.flush()

    for typ, up, content in loaded:
        name, sha = store_upload(up, content)
        db.add(
            Document(
                application_id=item.id,
                document_type=typ,
                original_name=(up.filename or "file")[:255],
                storage_name=name,
                mime_type=up.content_type or "application/octet-stream",
                size_bytes=len(content),
                sha256=sha,
            )
        )

    db.add(AuditLog(application_id=item.id, action="CREATED", details={"source": "public_form"}))
    db.commit()
    item = db.scalar(
        select(Application).options(selectinload(Application.documents)).where(Application.id == item.id)
    )
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
