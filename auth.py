"""
FALCON EYE - Authentication & Security Module
Implements password hashing with bcrypt, JWT token generation,
role-based access control, and audit logging.
"""

import os
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models import User, AuditLog

SECRET_KEY = os.getenv("SECRET_KEY", "FALCON_EYE_SECRET_KEY_SUPER_SECURE_98234")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for command room shifts

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[User]:
    """Get currently authenticated user, or fallback to default OPERATOR if token not provided in demo."""
    if not token:
        # For seamless hackathon demonstration, fallback to system operator if unauthenticated
        operator = db.query(User).filter(User.username == "operator").first()
        return operator

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.username == username).first()
    return user


def require_role(allowed_roles: list):
    """Dependency for role-based authorization."""
    def role_checker(current_user: Optional[User] = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication credentials were not provided."
            )
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation restricted. Requires one of roles: {allowed_roles}"
            )
        return current_user
    return role_checker


def log_audit(db: Session, action: str, entity_type: str, entity_id: str, details: str, username: str = "SYSTEM"):
    """Record an immutable action in the audit log."""
    log_entry = AuditLog(
        username=username,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        details=details,
        timestamp=datetime.utcnow()
    )
    db.add(log_entry)
    db.commit()
