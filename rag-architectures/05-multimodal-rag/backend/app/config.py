from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "multimodal-rag"
    environment: str = "development"
    log_level: str = "info"
    port: int = 8005

    # Auth
    secret_key: str = "super-secret-change-me"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # External services
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    postgres_url: str = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    ollama_url: str = "http://localhost:11434"

    # LLM / embeddings
    llm_model: str = "llama3:8b"
    embedding_model: str = "nomic-embed-text"

    # Multimodal retrieval
    multimodal_collection: str = "multimodal_rag"
    vector_size: int = 512
    default_top_k: int = 5

    # Media ingestion
    max_text_length: int = 100_000
    max_image_size_mb: int = 10
    max_audio_size_mb: int = 50
    supported_image_types: set[str] = {"image/jpeg", "image/png", "image/webp"}
    supported_audio_types: set[str] = {"audio/mpeg", "audio/wav", "audio/webm", "audio/mp4"}

    # Async processing
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    # Feature flags
    use_presidio: bool = False
    mock_embeddings: bool = False


settings = Settings()
