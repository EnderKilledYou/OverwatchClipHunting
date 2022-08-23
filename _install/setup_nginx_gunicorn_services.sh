#DOMAIN=$1
DOMAIN='hotface.city'
function install_certbot() {
  sudo certbot certonly -d $DOMAIN -d www.$DOMAIN --standalone --preferred-challenges http
}
function install_service {
  tee -a /etc/systemd/system/clip.service >/dev/null <<EOT
[Unit]
Description=Clip Hunta
After=network.target

[Service]
User=gamin
WorkingDirectory=/app
Environment="TESSERACT_DATA_FAST=/FAST_DATA/tessdata_fast/"
ExecStart=/home/sammy/myproject/myprojectenv/bin/gunicorn --workers 1 --threads 8 --timeout 0 --bind unix:clip.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
EOT
}
install_nginx_conf() {
  tee -a /etc/nginx/sites-available/$DOMAIN >/dev/null <<EOT
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        include proxy_params;
        proxy_pass http://unix:/app/clip.sock;
    }
}
EOT
}
enable_nginx_service() {
  ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled
  nginx -t
  systemctl restart nginx
}
enable_service() {
  systemctl enable clip
  systemctl start clip
}

install_nginx_conf

install_certbot

install_service

enable_nginx_service

enable_service
