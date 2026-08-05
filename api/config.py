"""App configuration — reads from environment variables."""


from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment
    environment: str = "local"  # local | production
    use_remote: bool = False
    app_version: str = "1.1.0"

    # PlantNet
    plantnet_api_key: str = ""
    plantnet_api_url: str = "https://my-api.plantnet.org/v2"

    # Supabase
    supabase_url: str = ""
    supabase_service_role_key: str = ""
    supabase_anon_key: str = ""

    # Auth security
    default_password: str = "12345678"
    login_max_attempts: int = 3
    login_lockout_seconds: int = 900
    reset_resend_cooldown_seconds: int = 60
    reset_pending_ttl_seconds: int = 86400
    reset_redirect_url: str = "gardenify://reset-password"

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

    @model_validator(mode="before")
    @classmethod
    def strip_env_whitespace(cls, values):
        """Strip whitespace from all env values (fixes Windows echo trailing spaces)."""
        return {k: v.strip() if isinstance(v, str) else v for k, v in values.items()}

    model_config = {"env_file": [".env", ".env.local"], "env_file_encoding": "utf-8", "extra": "ignore"}

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
