"""
CostLens – Security Utilities
JWT token creation / verification and password hashing.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# ── Password Helpers ──────────────────────────────────────────────

def _truncate_password(password: str, max_bytes: int = 72) -> str:
    """Truncate password to bcrypt's 72-byte limit at encoding level."""
    if isinstance(password, str):
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > max_bytes:
            # Truncate bytes and decode back to string
            password_bytes = password_bytes[:max_bytes]
            # Safely decode, removing any incomplete UTF-8 sequences
            password = password_bytes.decode('utf-8', errors='ignore')
    return password


def hash_password(password: str) -> str:
    """Hash password with bcrypt, handling 72-byte limit."""
    password = _truncate_password(password)
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against bcrypt hash."""
    plain = _truncate_password(plain)
    try:
        return pwd_context.verify(plain, hashed)
    except Exception:
        return False


# ── JWT Helpers ───────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
