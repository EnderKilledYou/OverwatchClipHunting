FROM ubuntu:18.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends tzdata
RUN apt-get update && apt-get install -y software-properties-common wget
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends  ca-certificates

RUN add-apt-repository -y ppa:alex-p/tesseract-ocr
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y tesseract-ocr-eng python3.8

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
RUN python3 -m pip install --no-cache-dir -r Requirements.txt

RUN chmod +x /app/startup.sh
RUN /app/startup.sh


# ENV zombie https://cliphunter-2f3vvue3ua-uw.a.run.app/nC8%2Al%24x4%2Boobm%3DEU5WJvZYu%3DPJXE9OBhP7%3D/
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app