import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://jesus:basededatos@localhost/gestiondb"
    SECRET_KEY: str = "pyua0h61iHL2-eNV4sZH1-rxa55ZIGpFstu0lSPWX8k"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 7

settings = Settings()