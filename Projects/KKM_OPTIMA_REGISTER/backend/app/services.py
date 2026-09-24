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
MAX_FILENAME_LENGTH = 255


def public_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def validate_file(data: bytes, mime: str) -> None:
    if mime not in ALLOWED_MIME:
        raise HTTPException(400, "Разрешены только PDF, JPG и PNG")
    if mime == "application/pdf" and not data.startswith(b"%PDF-"):
        raise HTTPException(400, "Файл не является корректным PDF")
    if mime == "image/jpeg" and not data.startswith(b"\xff\xd8\xff"):
        raise HTTPException(400, "Файл не является корректным JPEG")
    if mime == "image/png" and not data.startswith(b"\x89PNG\r\n\x1a\n"):
        raise HTTPException(400, "Файл не является корректным PNG")
    try:
        if mime == "application/pdf":
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted or not reader.pages:
                raise ValueError
        else:
            with Image.open(io.BytesIO(data)) as image:
                image.verify()
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise
        raise HTTPException(400, "Файл повреждён или имеет неверный формат") from exc


def load_upload(upload: UploadFile) -> bytes:
    return upload.file.read(s.max_file_size_mb * 1024 * 1024 + 1)


def store_upload(upload: UploadFile, data: bytes) -> tuple[str, str]:
    original = (upload.filename or "file")[:MAX_FILENAME_LENGTH]
    ext = Path(original).suffix.lower()
    ext = ext if ext in {".pdf", ".jpg", ".jpeg", ".png"} else ""
    name = f"{uuid4().hex}{ext}"
    root = Path(s.upload_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    path = (root / name).resolve()
    if path.parent != root:
        raise RuntimeError("Invalid upload path")
    path.write_bytes(data)
    return name, hashlib.sha256(data).hexdigest()


def remove_stored_files(names: list[str]) -> None:
    root = Path(s.upload_dir).resolve()
    for name in names:
        try:
            path = (root / name).resolve()
            if path.parent == root and path.is_file():
                path.unlink()
        except OSError:
            pass


def application_number() -> str:
    return "KKM-" + secrets.token_hex(5).upper()
