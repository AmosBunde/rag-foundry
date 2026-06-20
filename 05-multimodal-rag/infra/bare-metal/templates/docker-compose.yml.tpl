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

  celery-worker:
    image: ${app_image}
    container_name: ${project_name}-celery-worker
    restart: unless-stopped
    environment:
%{ for k, v in api_env ~}
      ${k}: "${v}"
%{ endfor ~}
    command: ["celery", "-A", "app.tasks", "worker", "-l", "info"]
    depends_on:
      redis:
        condition: service_started
      qdrant:
        condition: service_started
    networks:
      - ${docker_network}

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
%{ if ollama_enabled ~}
  ollama_data:
%{ endif ~}

networks:
  ${docker_network}:
    driver: bridge
    name: ${docker_network}
