from datetime import datetime,timedelta,timezone
import jwt
from cryptography.fernet import Fernet
from fastapi import Depends,HTTPException
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from pwdlib import PasswordHash
from .config import get_settings
from .db import get_db
from .models import Manager
s=get_settings();ph=PasswordHash.recommended();bearer=HTTPBearer(auto_error=False)
def _fernet():
 if not s.credential_encryption_key:raise RuntimeError('CREDENTIAL_ENCRYPTION_KEY is not configured')
 return Fernet(s.credential_encryption_key.encode())
def encrypt_secret(v):return _fernet().encrypt(v.encode()).decode()
def decrypt_secret(v):return _fernet().decrypt(v.encode()).decode()
def hash_password(v):return ph.hash(v)
def verify_password(v,h):return ph.verify(v,h)
def create_access_token(mid):return jwt.encode({'sub':mid,'exp':datetime.now(timezone.utc)+timedelta(minutes=s.access_token_minutes)},s.jwt_secret,algorithm='HS256')
def get_current_manager(credentials:HTTPAuthorizationCredentials|None=Depends(bearer),db=Depends(get_db)):
 if not credentials:raise HTTPException(401,'Требуется авторизация')
 try:mid=jwt.decode(credentials.credentials,s.jwt_secret,algorithms=['HS256']).get('sub')
 except jwt.PyJWTError:raise HTTPException(401,'Недействительный токен')
 m=db.get(Manager,mid)
 if not m or not m.is_active:raise HTTPException(401,'Менеджер не найден')
 return m
