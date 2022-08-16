FROM debian:bookworm-20220801 as BASE
#env
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VUE_HOME /app/front_end
ENV TESSERACT_DATA_FAST_INSTALL_FOLDER /FAST_DATA
ENV TESSERACT_DATA_FAST /FAST_DATA/tessdata_fast
ENV OCR_PRODUCTION True

FROM BASE as CERTSANDINSTALLS
RUN echo "basic stuff and certs"
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get  --no-install-recommends install -y git python3 python3-pip nodejs npm tzdata  software-properties-common ca-certificates ffmpeg libsm6 libxext6 cron tesseract-ocr
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates
RUN echo test software exists
RUN python3 -v
RUN python3 -m pip
RUN node -v

FROM CERTSANDINSTALLS as TESSY
RUN echo tesseract
WORKDIR $TESSERACT_DATA_FAST_INSTALL_FOLDER
RUN git clone https://github.com/tesseract-ocr/tessdata_fast.git


FROM TESSY as Work
RUN echo start copy files
WORKDIR $APP_HOME
COPY . ./

RUN echo build front end
WORKDIR $VUE_HOME
RUN npm install && npm run build

RUN echo build back end
WORKDIR $APP_HOME

RUN python3 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app