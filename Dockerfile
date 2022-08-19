FROM python:3.10-slim as BASE
ENV PYTHONUNBUFFERED True
ENV APP_HOME /app
ENV INSTALL_SCRIPT /app/_install/_install_tessy.sh
#Download Ocr Shit
ENV OCR_PRODUCTION True
ENV TESSERACT_DATA_FAST_INSTALL_FOLDER /FAST_DATA
ENV TESSERACT_DATA_FAST /FAST_DATA/tessdata_fast/
#print extra shit to console
ENV CLOUD_PRINT True
ARG DEBIAN_FRONTEND=noninteractive

FROM BASE as CERTSANDINSTALLS
RUN  apt-get update  &&  apt-get  -qq -y  --no-install-recommends   install git unzip ca-certificates ffmpeg libsm6 libxext6 tesseract-ocr  < /dev/null > /dev/null
RUN sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
RUN update-ca-certificates

FROM CERTSANDINSTALLS as RUNNER
WORKDIR $APP_HOME
COPY . ./
RUN chmod +x /app/_install/post_install.sh
RUN chmod +x /app/_install/_install_tessy.sh
RUN /app/_install/post_install.sh
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app


