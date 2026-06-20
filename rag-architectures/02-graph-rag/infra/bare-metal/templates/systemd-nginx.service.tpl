[Unit]
Description=Nginx reverse proxy for ${project_name}
After=docker.service

[Service]
Restart=always
ExecStartPre=-/usr/bin/docker rm -f ${project_name}-nginx
ExecStart=/usr/bin/docker run --name ${project_name}-nginx --network host \
  -v ${deploy_path}/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
%{ if enable_https ~}
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
%{ endif ~}
  nginx:alpine
ExecStop=-/usr/bin/docker stop ${project_name}-nginx
ExecStopPost=-/usr/bin/docker rm ${project_name}-nginx

[Install]
WantedBy=multi-user.target
