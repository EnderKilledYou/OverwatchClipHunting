git pull
sudo gunicorn --bind :80 --workers 1 --threads 8 --timeout 0 app:app  > log.txt 2>&1
