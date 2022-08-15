chmod 0644 /etc/cron.d/backup-cron
crontab /etc/cron.d/backup-cron
python3 startup_file.py