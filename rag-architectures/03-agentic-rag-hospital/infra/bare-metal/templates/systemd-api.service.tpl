[Unit]
Description=${project_name} Agentic RAG Hospital API (Docker Compose)
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=${deploy_path}
ExecStart=/usr/bin/docker compose -f docker-compose.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.yml down
ExecReload=/usr/bin/docker compose -f docker-compose.yml up -d
TimeoutStartSec=300

[Install]
WantedBy=multi-user.target
