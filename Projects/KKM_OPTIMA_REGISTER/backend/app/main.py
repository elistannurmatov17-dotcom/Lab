from collections import defaultdict, deque
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, HTTPException, Request, Response
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from .auth import hash_password, verify_password
from .config import get_settings
from .db import Base, engine
from .models import Manager
from .routes_manager import router as manager_router
from .routes_public import router as public_router

s = get_settings()


class SimpleRateLimitMiddleware:
    def __init__(self, app, public_per_minute: int = 20, login_per_minute: int = 10):
        self.app = app
        self.public_per_minute = public_per_minute
        self.login_per_minute = login_per_minute
        self.buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    @staticmethod
    def _client_ip(request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        return forwarded.split(",", 1)[0].strip() if forwarded else (request.client.host if request.client else "unknown")

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        path = request.url.path
        if path == "/api/auth/login":
            limit = self.login_per_minute
            bucket_name = "login"
        elif path == "/api/applications" or path.startswith("/api/public/"):
            limit = self.public_per_minute
            bucket_name = "public"
        else:
            await self.app(scope, receive, send)
            return

        key = (bucket_name, self._client_ip(request))
        now = monotonic()
        bucket = self.buckets[key]
        while bucket and now - bucket[0] >= 60:
            bucket.popleft()
        if len(bucket) >= limit:
            response = Response("Слишком много запросов. Попробуйте позже.", status_code=429)
            await response(scope, receive, send)
            return
        bucket.append(now)
        if len(self.buckets) > 5000:
            self.buckets = defaultdict(deque, {k: v for k, v in self.buckets.items() if v and now - v[-1] < 60})
        await self.app(scope, receive, send)


production = s.environment.lower() == "production"
app = FastAPI(
    title=s.app_name,
    version="1.0.0",
    docs_url=None if production else "/docs",
    redoc_url=None if production else "/redoc",
    openapi_url=None if production else "/openapi.json",
)
app.add_middleware(SimpleRateLimitMiddleware)
app.include_router(public_router)
app.include_router(manager_router)


@app.on_event("startup")
def startup() -> None:
    if not s.jwt_secret or not s.credential_encryption_key:
        raise RuntimeError("JWT_SECRET and CREDENTIAL_ENCRYPTION_KEY are required")
    if production and s.environment.lower() != "production":
        raise RuntimeError("Invalid production configuration")
    Base.metadata.create_all(bind=engine)
    if production:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS internal_comment TEXT"))
            conn.execute(text("ALTER TABLE applications ADD COLUMN IF NOT EXISTS ugns_other VARCHAR(255)"))
    Path(s.upload_dir).mkdir(parents=True, exist_ok=True)

    with Session(engine) as db:
        for username, password in [
            (s.manager_1_username, s.manager_1_password),
            (s.manager_2_username, s.manager_2_password),
            (s.manager_3_username, s.manager_3_password),
        ]:
            if not username or not password:
                continue
            manager = db.scalar(select(Manager).where(Manager.username == username))
            if not manager:
                db.add(Manager(username=username, password_hash=hash_password(password)))
            elif not verify_password(password, manager.password_hash):
                manager.password_hash = hash_password(password)
        db.commit()


@app.get("/health")
def health() -> dict[str, str]:
    try:
        with Session(engine) as db:
            db.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(503, "Database unavailable") from exc
    return {"status": "ok"}
