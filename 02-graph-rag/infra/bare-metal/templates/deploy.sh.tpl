#!/usr/bin/env bash
set -euo pipefail

HOST="${host_user}@${host_ip}"
DEPLOY_PATH="${deploy_path}"

ssh -i "${ssh_private_key_path}" "$HOST" "mkdir -p ${deploy_path}"

scp -i "${ssh_private_key_path}" \
  out/docker-compose.yml \
  out/nginx.conf \
  out/graph-rag-api.service \
  out/graph-rag-nginx.service \
  out/.env \
  "$HOST:${deploy_path}/"

%{ if enable_https ~}
ssh -i "${ssh_private_key_path}" "$HOST" "
  sudo apt-get update
  sudo apt-get install -y certbot
  sudo certbot certonly --standalone -d ${domain} --agree-tos -m ${admin_email} --non-interactive || true
"
%{ endif ~}

ssh -i "${ssh_private_key_path}" "$HOST" "
  cd ${deploy_path}
  sudo cp graph-rag-api.service /etc/systemd/system/
  sudo cp graph-rag-nginx.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable graph-rag-api graph-rag-nginx
  sudo systemctl start graph-rag-api graph-rag-nginx
"
