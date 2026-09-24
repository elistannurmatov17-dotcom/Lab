from pathlib import Path
from fastapi import FastAPI
from sqlalchemy import select
from sqlalchemy.orm import Session
from .config import get_settings
from .db import Base, engine
from .auth import hash_password
from .models import Manager
from .routes_public import router as public_router
from .routes_manager import router as manager_router

s = get_settings()
app = FastAPI(title=s.app_name, version="0.1.0")
app.include_router(public_router)
app.include_router(manager_router)

@app.on_event("startup")
def startup():
    if not s.jwt_secret or not s.credential_encryption_key:
        raise RuntimeError("JWT_SECRET and CREDENTIAL_ENCRYPTION_KEY are required")
    Base.metadata.create_all(bind=engine)
    Path(s.upload_dir).mkdir(parents=True, exist_ok=True)
    if s.environment == "development":
        with Session(engine) as db:
            for username, password in [
                (s.manager_1_username, s.manager_1_password),
                (s.manager_2_username, s.manager_2_password),
                (s.manager_3_username, s.manager_3_password),
            ]:
                if username and password and not db.scalar(select(Manager).where(Manager.username == username)):
                    db.add(Manager(username=username, password_hash=hash_password(password)))
            db.commit()

@app.get("/health")
def health():
    return {"status": "ok"}
