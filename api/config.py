import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    plantnet_api_key: str = ""
    plantnet_api_url: str = "https://my-api.plantnet.org/v2"
    supabase_url: str = ""
    supabase_service_key: str = ""
    cors_origins: list[str] = ["http://localhost:8081", "http://localhost:19006"]
    max_images: int = 5
    max_image_size_mb: int = 10
    max_total_size_mb: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
