[Unit]
Description=Agentic RAG Hospital Nginx Reverse Proxy
Requires=docker.service
After=docker.service

[Service]
Restart=always
ExecStartPre=-/usr/bin/docker rm -f agentic-rag-hospital-nginx
ExecStart=/usr/bin/docker run \
    --name agentic-rag-hospital-nginx \
    --network host \
    -v ${deploy_path}/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
    -v ${deploy_path}/certbot-data/etc/letsencrypt:/etc/letsencrypt:ro \
    -v ${deploy_path}/certbot-data/var/www/certbot:/var/www/certbot:ro \
    -p 80:80 -p 443:443 \
    nginx:alpine
ExecStop=-/usr/bin/docker stop agentic-rag-hospital-nginx
ExecStopPost=-/usr/bin/docker rm -f agentic-rag-hospital-nginx

[Install]
WantedBy=multi-user.target
