from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    upload_dir: str = "uploads"
    max_upload_size: int = 262144000  # 250 MB
    
    model_config = ConfigDict(env_file=".env")

settings = Settings()