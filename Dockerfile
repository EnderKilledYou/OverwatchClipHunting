FROM ubuntu:18.04
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y  tzdata  software-properties-common curl

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends  ca-certificates
RUN DEBIAN_FRONTEND=noninteractive apt-get install  ffmpeg libsm6 libxext6 cron -y
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates
RUN curl -sL https://deb.nodesource.com/setup_16.x -o /tmp/nodesource_setup.sh
RUN bash /tmp/nodesource_setup.sh
RUN apt install nodejs -y

RUN add-apt-repository  ppa:deadsnakes/ppa
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y python3.8 tesseract-ocr python3-pip


ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./



RUN curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && apt-get install yarn -y
WORKDIR /app/front_end
RUN yarn install && yarn run build
WORKDIR /app/
RUN python3.8 -m pip install --upgrade pip
RUN python3.8 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app