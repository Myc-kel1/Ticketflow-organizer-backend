from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    ENV: str = "development"
    DEBUG: bool = False
    API_PREFIX: str 

    SUPABASE_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_JWT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",   
    )


settings = Settings()
__all__ = ["settings"]