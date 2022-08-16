FROM ubuntu:18.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends tzdata curl
RUN apt-get update && apt-get install -y software-properties-common wget
RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
RUN bash /tmp/nodesource_setup.sh
RUN apt install nodejs -y
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends  ca-certificates
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y python3.8
RUN add-apt-repository ppa:alex-p/tesseract-ocr5
RUN apt-get update && apt-get install -y tesseract-ocr

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./
COPY backup-cron /etc/cron.d/backup-cron
RUN apt update -y
RUN apt upgrade -y
RUN apt install python3 python3-pip -y
RUN apt-get install python3 python3-pip ffmpeg libsm6 libxext6 ca-certificates  cron -y
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates

RUN npm install -g npm -y
RUN tesseract --help
RUN curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update -y && apt-get install yarn -y
WORKDIR /app/front_end
RUN yarn install
RUN yarn run build
WORKDIR /app/
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --no-cache-dir -r Requirements.txt
RUN chmod +x /app/startup.sh
RUN /app/startup.sh
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app