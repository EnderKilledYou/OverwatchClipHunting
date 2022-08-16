FROM debian:bookworm-20220801
#env
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VUE_HOME /app/front_end
ENV PRODUCTION True

# basic stuff and certs
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y  tzdata  software-properties-common ca-certificates ffmpeg libsm6 libxext6 cron tesseract-ocr
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates

#python
RUN python3 -v


#start copy files
WORKDIR $APP_HOME
COPY . ./

# build front end
WORKDIR $VUE_HOME
RUN npm install && npm run build

# build back end
WORKDIR $APP_HOME
RUN python3.8 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app