"""User authentication and token management."""
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel
import jwt

from app.config import settings
from app.logger import get_logger

logger = get_logger(__name__)
security = HTTPBearer()


class TokenData(BaseModel):
    user_id: str
    username: str
    exp: datetime


def create_access_token(user_id: str, username: str) -> str:
    """Create a signed JWT token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(credentials: Annotated[HTTPAuthCredentials, Depends(security)]) -> TokenData:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("user_id")
        username = payload.get("username")
        if not user_id or not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return TokenData(user_id=user_id, username=username, exp=payload.get("exp"))
    except jwt.ExpiredSignatureError as exc:
        logger.warning(f"Token expired for user")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired") from exc
    except jwt.InvalidTokenError as exc:
        logger.error(f"Invalid token received")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
