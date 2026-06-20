#!/usr/bin/env bash
set -euo pipefail

HOST="$${HOST:-${host_ip}}"
USER="$${USER:-${host_user}}"
KEY="$${KEY:-${ssh_private_key_path}}"
DEPLOY_PATH="$${DEPLOY_PATH:-${deploy_path}}"
DOMAIN="$${DOMAIN:-${domain}}"
EMAIL="$${EMAIL:-${admin_email}}"

ssh -i "$${KEY}" -o StrictHostKeyChecking=no "$${USER}@$${HOST}" "
  set -e
  sudo mkdir -p ${deploy_path}/certbot-data/etc/letsencrypt
  sudo mkdir -p ${deploy_path}/certbot-data/var/www/certbot
"

scp -i "$${KEY}" -o StrictHostKeyChecking=no -r \
  out/docker-compose.yml \
  out/nginx.conf \
  out/.env \
  "$${USER}@$${HOST}:/tmp/hybrid-rag-deploy/"

ssh -i "$${KEY}" -o StrictHostKeyChecking=no "$${USER}@$${HOST}" "
  set -e
  sudo mv /tmp/hybrid-rag-deploy/* ${deploy_path}/
  sudo chown -R root:root ${deploy_path}

%{ if enable_https ~}
  # Obtain or renew certificate
  sudo docker run --rm -it \\
    -v ${deploy_path}/certbot-data/etc/letsencrypt:/etc/letsencrypt \\
    -v ${deploy_path}/certbot-data/var/www/certbot:/var/www/certbot \\
    certbot/certbot certonly \\
      --standalone \\
      --agree-tos \\
      --no-eff-email \\
      -m ${admin_email} \\
      -d ${domain} \\
      || true
%{ endif ~}

  sudo cp ${deploy_path}/hybrid-rag-api.service /etc/systemd/system/
  sudo cp ${deploy_path}/hybrid-rag-nginx.service /etc/systemd/system/
  sudo systemctl daemon-reload
  sudo systemctl enable --now hybrid-rag-api hybrid-rag-nginx
"

echo "Deployment complete. API available at https://$${DOMAIN}"
