from jose import JWTError, jwt

from app.core.config import settings


# JWT token decode qilish
def decode_access_token(token: str) -> dict:
    try:

        # JWT tokenni decode qilamiz
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )

    except JWTError as exc:

        # Token noto'g'ri bo'lsa
        raise ValueError("Invalid token") from exc