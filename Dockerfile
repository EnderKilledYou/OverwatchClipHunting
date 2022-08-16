FROM debian:bookworm-20220801 as BASE
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV VUE_HOME /app/front_end
ENV TESSERACT_DATA_FAST_INSTALL_FOLDER /FAST_DATA
ENV TESSERACT_DATA_FAST /FAST_DATA/tessdata_fast
ENV OCR_PRODUCTION True

FROM BASE as CERTSANDINSTALLS
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get  --no-install-recommends install -y git python3 python3-pip nodejs npm tzdata ca-certificates ffmpeg libsm6 libxext6 cron tesseract-ocr
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates
RUN echo test software exists
RUN python3 -v
RUN python3 -m pip
RUN node -v



FROM CERTSANDINSTALLS as COPYFILES
WORKDIR $APP_HOME
COPY . ./



FROM CERTSANDINSTALLS as STARTGUN
WORKDIR $APP_HOME
RUN python3 -m pip install --no-cache-dir -r Requirements.txt

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app