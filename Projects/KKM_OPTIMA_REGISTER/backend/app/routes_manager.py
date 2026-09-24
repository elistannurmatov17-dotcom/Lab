from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .auth import create_access_token, decrypt_secret, get_current_manager, verify_password
from .config import get_settings
from .db import get_db
from .models import Application, AuditLog, Document, Manager
from .schemas import ApplicationDetails, ApplicationListItem, AssignManager, AuditEvent, ManagerOut, StatusUpdate, TokenResponse

router = APIRouter(prefix="/api")
s = get_settings()
STAT = {"NEW", "IN_PROGRESS", "WAITING_CLIENT", "PROCESSING", "COMPLETED", "REJECTED"}


@router.post("/auth/login", response_model=TokenResponse)
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    manager = db.scalar(select(Manager).where(Manager.username == username, Manager.is_active == True))
    if not manager or not verify_password(password, manager.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    return TokenResponse(access_token=create_access_token(manager.id))


@router.get("/auth/me", response_model=ManagerOut)
def me(manager=Depends(get_current_manager)):
    return manager


@router.get("/applications", response_model=list[ApplicationListItem])
def applications(
    status_filter: str | None = None,
    manager_id: str | None = None,
    manager=Depends(get_current_manager),
    db: Session = Depends(get_db),
):
    query = select(Application).order_by(Application.created_at.desc())
    if status_filter:
        query = query.where(Application.status == status_filter)
    if manager_id:
        query = query.where(Application.manager_id == manager_id)
    return list(db.scalars(query).all())


@router.get("/applications/{application_id}", response_model=ApplicationDetails)
def get_application(application_id: str, manager=Depends(get_current_manager), db: Session = Depends(get_db)):
    item = db.scalar(
        select(Application).options(selectinload(Application.documents)).where(Application.id == application_id)
    )
    if not item:
        raise HTTPException(404, "Заявка не найдена")
    return ApplicationDetails.model_validate(item, from_attributes=True)


@router.get("/applications/{application_id}/audit", response_model=list[AuditEvent])
def audit(application_id: str, manager=Depends(get_current_manager), db: Session = Depends(get_db)):
    if not db.get(Application, application_id):
        raise HTTPException(404, "Заявка не найдена")
    return list(db.scalars(
        select(AuditLog).where(AuditLog.application_id == application_id).order_by(AuditLog.created_at.desc())
    ).all())


@router.get("/applications/{application_id}/credentials")
def credentials(application_id: str, manager=Depends(get_current_manager), db: Session = Depends(get_db)):
    item = db.get(Application, application_id)
    if not item:
        raise HTTPException(404, "Заявка не найдена")
    db.add(AuditLog(application_id=item.id, actor_manager_id=manager.id, action="CREDENTIALS_VIEWED", details={}))
    db.commit()
    return {"login": item.login, "password": decrypt_secret(item.lk_password_encrypted)}


@router.patch("/applications/{application_id}/status", response_model=ApplicationDetails)
def update_status(
    application_id: str,
    payload: StatusUpdate,
    manager=Depends(get_current_manager),
    db: Session = Depends(get_db),
):
    item = db.scalar(
        select(Application).options(selectinload(Application.documents)).where(Application.id == application_id)
    )
    if not item:
        raise HTTPException(404, "Заявка не найдена")
    old = item.status
    item.status = payload.status
    if payload.comment is not None:
        item.comment = payload.comment
    if payload.internal_comment is not None:
        item.internal_comment = payload.internal_comment
    db.add(AuditLog(
        application_id=item.id,
        actor_manager_id=manager.id,
        action="STATUS_CHANGED",
        details={"from": old, "to": payload.status},
    ))
    db.commit()
    db.refresh(item)
    return ApplicationDetails.model_validate(item, from_attributes=True)


@router.patch("/applications/{application_id}/assign", response_model=ApplicationDetails)
def assign(
    application_id: str,
    payload: AssignManager,
    manager=Depends(get_current_manager),
    db: Session = Depends(get_db),
):
    item = db.scalar(select(Application).options(selectinload(Application.documents)).where(Application.id == application_id))
    assignee = db.get(Manager, payload.manager_id)
    if not item or not assignee or not assignee.is_active:
        raise HTTPException(404, "Заявка или менеджер не найдены")
    old_manager = item.manager_id
    item.manager_id = assignee.id
    db.add(AuditLog(
        application_id=item.id,
        actor_manager_id=manager.id,
        action="ASSIGNED",
        details={"from_manager_id": old_manager, "to_manager_id": assignee.id},
    ))
    db.commit()
    db.refresh(item)
    return ApplicationDetails.model_validate(item, from_attributes=True)


@router.get("/managers", response_model=list[ManagerOut])
def managers(manager=Depends(get_current_manager), db: Session = Depends(get_db)):
    return list(db.scalars(select(Manager).where(Manager.is_active == True).order_by(Manager.username)).all())


@router.get("/applications/{application_id}/documents/{document_id}")
def document(
    application_id: str,
    document_id: str,
    manager=Depends(get_current_manager),
    db: Session = Depends(get_db),
):
    doc = db.scalar(select(Document).where(Document.id == document_id, Document.application_id == application_id))
    if not doc:
        raise HTTPException(404, "Документ не найден")
    root = Path(s.upload_dir).resolve()
    path = (root / doc.storage_name).resolve()
    if path.parent != root or not path.is_file():
        raise HTTPException(404, "Файл отсутствует")
    db.add(AuditLog(
        application_id=application_id,
        actor_manager_id=manager.id,
        action="DOCUMENT_VIEWED",
        details={"document_id": document_id},
    ))
    db.commit()
    return FileResponse(path, media_type=doc.mime_type, filename=doc.original_name)
