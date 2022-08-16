FROM debian:bookworm-20220801
#env
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VUE_HOME /app/front_end
ENV TESSERACT_DATA_FAST_INSTALL_FOLDER /FAST_DATA
ENV TESSERACT_DATA_FAST /FAST_DATA/tessdata_fast
ENV PRODUCTION True

# basic stuff and certs
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get  --no-install-recommends install -y git python3 nodejs npm tzdata  software-properties-common ca-certificates ffmpeg libsm6 libxext6 cron tesseract-ocr
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates

#python
RUN python3 -v

RUN node -v

WORKDIR $TESSERACT_DATA_FAST
RUN git clone https://github.com/tesseract-ocr/tessdata_fast.git

#start copy files
WORKDIR $APP_HOME
COPY . ./

# build front end
WORKDIR $VUE_HOME
RUN npm install && npm run build

# build back end
WORKDIR $APP_HOME
RUN python3 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app