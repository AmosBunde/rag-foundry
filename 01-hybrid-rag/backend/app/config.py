from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "hybrid-rag"
    environment: str = "development"
    log_level: str = "info"
    port: int = 8001

    # Auth
    secret_key: str = "super-secret-change-me"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # External services
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    elasticsearch_url: str = "http://localhost:9200"
    postgres_url: str = "postgresql+asyncpg://rag:rag@localhost:5432/rag"
    ollama_url: str = "http://localhost:11434"

    # LLM
    llm_model: str = "llama3:8b"
    embedding_model: str = "nomic-embed-text"

    # Retrieval
    dense_collection: str = "hybrid_rag_dense"
    sparse_index: str = "hybrid_rag_sparse"
    default_top_k: int = 5


settings = Settings()
