FROM debian:bookworm-20220801
#env
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VUE_HOME /app/front_end
ENV PRODUCTION True

# basic stuff and certs
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y  tzdata  software-properties-common ca-certificates ffmpeg libsm6 libxext6 cron
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates


# node and yarn
COPY setup_node_16.sh .
RUN bash ./setup_node_16.sh
RUN apt install nodejs -y
RUN curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null
RUN echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && apt-get install yarn -y

RUN python -v
#python
RUN add-apt-repository  ppa:deadsnakes/ppa
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y python3.8 tesseract-ocr python3-pip
RUN python3.8 -m pip install --upgrade pip

#start copy files
WORKDIR $APP_HOME
COPY . ./

# build front end
WORKDIR $VUE_HOME
RUN yarn install && yarn run build


# build back end
WORKDIR $APP_HOME
RUN python3.8 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app