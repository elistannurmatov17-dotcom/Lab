import hashlib
import io
import secrets
from pathlib import Path
from uuid import uuid4
from fastapi import HTTPException, UploadFile
from PIL import Image
from pypdf import PdfReader
from .config import get_settings

s = get_settings()
ALLOWED_MIME = {"application/pdf", "image/jpeg", "image/png"}

def public_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def validate_file(data: bytes, mime: str):
    if mime not in ALLOWED_MIME:
        raise HTTPException(400, "Разрешены только PDF, JPG и PNG")
    try:
        if mime == "application/pdf":
            r = PdfReader(io.BytesIO(data))
            if r.is_encrypted or not r.pages:
                raise ValueError
        else:
            Image.open(io.BytesIO(data)).verify()
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(400, "Файл повреждён или имеет неверный формат")

def load_upload(up: UploadFile):
    return up.file.read(s.max_file_size_mb * 1024 * 1024 + 1)

def store_upload(up: UploadFile, data: bytes):
    ext = Path(up.filename or "file").suffix.lower()
    ext = ext if ext in {".pdf", ".jpg", ".jpeg", ".png"} else ""
    name = uuid4().hex + ext
    path = Path(s.upload_dir) / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return name, hashlib.sha256(data).hexdigest()

def application_number():
    return "KKM-" + secrets.token_hex(5).upper()
