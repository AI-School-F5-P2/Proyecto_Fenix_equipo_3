from pydantic_settings import BaseSettings
from dotenv import load_dotenv  # solo si quieres cargar .env manualmente (opcional)
import os

# Opcional si no se carga automáticamente (pero normalmente no hace falta con pydantic_settings)
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    GOOGLE_CX: str
    OPENROUTER_API_KEY: str
    YOUTUBE_API_KEY: str 
    SECRET_KEY: str
    ALGORITHM:str
    ACCESS_TOKEN_EXPIRE_MINUTES: int


    class Config:
        env_file = ".env"  # Pydantic buscará aquí las variables

settings = Settings()