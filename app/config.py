import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://admin:91Durk9bruMN3mfKZG99cmx0sLA8Sfzn@dpg-cut7855umphs73cg3u2g-a.oregon-postgres.render.com/basededatos_wp0n"
    SECRET_KEY: str = "pyua0h61iHL2-eNV4sZH1-rxa55ZIGpFstu0lSPWX8k"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 15

settings = Settings()