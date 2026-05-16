from pydantic_settings import BaseSettings, SettingsConfigDict


# Application config classi
class Settings(BaseSettings):

    # Database connection URL
    database_url: str

    # JWT secret key
    jwt_secret_key: str

    # JWT algorithm
    jwt_algorithm: str = "HS256"

    # Access token expire vaqti (minute)
    access_token_expire_minutes: int = 60

    # .env file configlari
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


# Global settings object
settings = Settings()