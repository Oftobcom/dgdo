from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hash config
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
)


# Passwordni hash qilish
def hash_password(password: str) -> str:
    return pwd_context.hash(password)


# Passwordni verify qilish
def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


# JWT access token yaratish
def create_access_token(subject: str) -> str:

    # Token expire vaqtini hisoblaymiz
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )

    # JWT payload
    payload = {
        "sub": subject,  # User ID
        "exp": expire,   # Expire time
    }

    # JWT token encode qilamiz
    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


# JWT token decode qilish
def decode_access_token(token: str) -> dict:
    try:

        # JWT token decode qilamiz
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except JWTError as exc:

        # Token noto'g'ri bo'lsa
        raise ValueError("Invalid token") from exc