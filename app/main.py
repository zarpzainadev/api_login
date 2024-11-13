# app/main.py
import logging
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
from app.api.endpoints import auth
from app.database import engine
from sqlalchemy import text
from fastapi.middleware.cors import CORSMiddleware

security = HTTPBearer()

app = FastAPI(title="Auth API")


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)



def verify_database_connection():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Conexión a la base de datos establecida correctamente.")
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise

@app.on_event("startup")
async def startup_event():
    verify_database_connection()


# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])