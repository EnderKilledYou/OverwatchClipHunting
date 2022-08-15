FROM clearlinux/tesseract-ocr

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
COPY backup-cron /etc/cron.d/backup-cron

RUN chmod +x /app/install_debian.sh
RUN /app/install_debian.sh

# Install production dependencies.
RUN pip install --no-cache-dir -r Requirements.txt

RUN chmod +x /app/startup.sh
RUN /app/startup.sh


# ENV zombie https://cliphunter-2f3vvue3ua-uw.a.run.app/nC8%2Al%24x4%2Boobm%3DEU5WJvZYu%3DPJXE9OBhP7%3D/
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app