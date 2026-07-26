"""App configuration — reads from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # PlantNet
    plantnet_api_key: str = ""
    plantnet_api_url: str = "https://my-api.plantnet.org/v2"

    # Supabase
    supabase_url: str = ""
    supabase_service_key: str = ""

    # Limits
    max_images: int = 5
    max_image_size_mb: int = 10

    # Dev
    debug: bool = False
    cors_origins: list[str] = [
        "http://localhost:8081",
        "http://localhost:19006",
        "http://localhost:3000",
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
