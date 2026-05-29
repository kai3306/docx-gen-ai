from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "dev-secret-key-change-in-production-abc123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DIFY_API_URL: str = "http://localhost:8080/v1"
    DIFY_API_KEY: str = "mock-dify-key"
    MOCK_DIFY: bool = True

    UPLOAD_DIR: str = "./uploads"
    TEMPLATE_DIR: str = "../templates"
    GENERATED_DIR: str = "../generated"

    class Config:
        env_file = ".env"


settings = Settings()
