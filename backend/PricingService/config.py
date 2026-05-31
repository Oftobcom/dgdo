# config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from decimal import Decimal

class Settings(BaseSettings):
    economy_base_fee: Decimal
    economy_per_km: Decimal
    economy_per_min: Decimal
    economy_min_fare: Decimal
    economy_max_surge: Decimal

    comfort_base_fee: Decimal
    comfort_per_km: Decimal
    comfort_per_min: Decimal
    comfort_min_fare: Decimal
    comfort_max_surge: Decimal

    xl_base_fee: Decimal
    xl_per_km: Decimal
    xl_per_min: Decimal
    xl_min_fare: Decimal
    xl_max_surge: Decimal

    delivery_base_fee: Decimal
    delivery_per_km: Decimal
    delivery_per_min: Decimal
    delivery_min_fare: Decimal
    delivery_max_surge: Decimal

    default_currency: str = "TJS"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()