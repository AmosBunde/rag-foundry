upstream api_backend {
    server 127.0.0.1:${api_port};
    keepalive 32;
}

server {
    listen 80;
    server_name ${domain};

%{ if enable_https ~}
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://$${server_name}$${request_uri};
    }
}

server {
    listen 443 ssl http2;
    server_name ${domain};

    ssl_certificate     /etc/letsencrypt/live/${domain}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/${domain}/privkey.pem;
    include             /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam         /etc/letsencrypt/ssl-dhparams.pem;

    client_max_body_size 50M;

    location / {
        proxy_pass         http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header   Connection "";
        proxy_set_header   Host $${host};
        proxy_set_header   X-Real-IP $${remote_addr};
        proxy_set_header   X-Forwarded-For $${proxy_add_x_forwarded_for};
        proxy_set_header   X-Forwarded-Proto $${scheme};
        proxy_read_timeout 300s;
    }
}
%{ else ~}
    client_max_body_size 50M;

    location / {
        proxy_pass         http://api_backend;
        proxy_http_version 1.1;
        proxy_set_header   Connection "";
        proxy_set_header   Host $${host};
        proxy_set_header   X-Real-IP $${remote_addr};
        proxy_set_header   X-Forwarded-For $${proxy_add_x_forwarded_for};
        proxy_set_header   X-Forwarded-Proto $${scheme};
        proxy_read_timeout 300s;
    }
}
%{ endif ~}
