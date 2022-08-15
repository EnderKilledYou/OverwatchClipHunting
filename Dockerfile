FROM franky1/tesseract

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


# ENV zombie main_host
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app