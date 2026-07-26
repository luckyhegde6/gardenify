"""App configuration — reads from environment variables."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = "local"  # local | production
    use_remote: bool = False  # True = connect to prod Supabase from local backend

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

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def supabase_effective_url(self) -> str:
        """When USE_REMOTE=true, always use prod Supabase URL."""
        if self.use_remote and self.supabase_url.startswith("http://localhost"):
            raise ValueError(
                "USE_REMOTE=true but SUPABASE_URL is localhost. "
                "Set SUPABASE_URL to your production Supabase project URL."
            )
        return self.supabase_url


settings = Settings()
