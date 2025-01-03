import secrets
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://gestion_s5g7_user:oqoTqK5PLSasXvqSj5q34iTQf7ufvPt0@dpg-ctjn22dsvqrc7389ui3g-a.oregon-postgres.render.com/gestion_s5g7"
    SECRET_KEY: str = "pyua0h61iHL2-eNV4sZH1-rxa55ZIGpFstu0lSPWX8k"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 15

settings = Settings()