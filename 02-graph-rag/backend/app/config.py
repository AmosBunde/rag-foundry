from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "graph-rag"
    environment: str = "development"
    log_level: str = "info"
    port: int = 8002

    # Auth
    secret_key: str = "super-secret-change-me"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"

    # External services
    redis_url: str = "redis://localhost:6379/0"
    qdrant_url: str = "http://localhost:6333"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "ragfoundry"
    ollama_url: str = "http://localhost:11434"

    # LLM / embeddings
    llm_model: str = "llama3:8b"
    embedding_model: str = "nomic-embed-text"

    # Retrieval / graph
    graph_collection: str = "graph_rag_chunks"
    default_top_k: int = 5
    graph_depth: int = 2
    max_entities_per_chunk: int = 20


settings = Settings()
