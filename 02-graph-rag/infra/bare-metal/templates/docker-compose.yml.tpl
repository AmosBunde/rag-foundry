services:
  api:
    image: ${app_image}
    container_name: ${project_name}-api
    restart: unless-stopped
    environment:
%{ for k, v in api_env ~}
      ${k}: "${v}"
%{ endfor ~}
    ports:
      - "127.0.0.1:${api_port}:${api_port}"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_started
      qdrant:
        condition: service_started
      neo4j:
        condition: service_healthy
    networks:
      - ${docker_network}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${api_port}/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  postgres:
    image: postgres:16-alpine
    container_name: ${project_name}-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: ${postgres_user}
      POSTGRES_PASSWORD: ${postgres_password}
      POSTGRES_DB: ${postgres_db}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - ${docker_network}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${postgres_user} -d ${postgres_db}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: ${project_name}-redis
    restart: unless-stopped
    command: >
      sh -c "redis-server --requirepass ${redis_password} --appendonly yes"
    volumes:
      - redis_data:/data
    networks:
      - ${docker_network}

  qdrant:
    image: qdrant/qdrant:latest
    container_name: ${project_name}-qdrant
    restart: unless-stopped
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - ${docker_network}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 15s
      timeout: 5s
      retries: 5

  neo4j:
    image: neo4j:5.19-community
    container_name: ${project_name}-neo4j
    restart: unless-stopped
    environment:
      NEO4J_AUTH: neo4j/${neo4j_password}
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    networks:
      - ${docker_network}
    healthcheck:
      test: ["CMD-SHELL", "cypher-shell -u neo4j -p ${neo4j_password} 'RETURN 1'"]
      interval: 20s
      timeout: 10s
      retries: 10

%{ if ollama_enabled ~}
  ollama:
    image: ${ollama_image}
    container_name: ${project_name}-ollama
    restart: unless-stopped
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - ${docker_network}
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    entrypoint: >
      sh -c "ollama serve &
             sleep 5
%{ for model in ollama_models ~}
             ollama pull ${model}
%{ endfor ~}
             wait"
%{ endif ~}

volumes:
  postgres_data:
  redis_data:
  qdrant_data:
  neo4j_data:
  neo4j_logs:
%{ if ollama_enabled ~}
  ollama_data:
%{ endif ~}

networks:
  ${docker_network}:
    driver: bridge
    name: ${docker_network}
