chmod 0644 /etc/cron.d/backup-cron
crontab /etc/cron.d/backup-cron
/etc/init.d/cron start

cd /app/front_end/
npm install && npm run build
python3.8 startup_file.py
