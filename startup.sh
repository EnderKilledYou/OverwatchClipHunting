chmod 0644 /etc/cron.d/backup-cron
crontab /etc/cron.d/backup-cron
python startup_file.py