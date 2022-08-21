FROM python:3.10-slim as BASE
export PYTHONUNBUFFERED=True
export APP_HOME=/app
#export INSTALL_SCRIPT /app/_install/install_tessy.sh
#Download Ocr Shit
export OCR_PRODUCTION=True
export TESSERACT_DATA_FAST_INSTALL_FOLDER=/FAST_DATA
export TESSERACT_DATA_FAST=/FAST_DATA/tessdata_fast/
#print extra shit to console
export CLOUD_PRINT=True

apt-get update && apt-get -qq -y --no-install-recommends install pip git unzip ca-certificates ffmpeg libsm6 libxext6 tesseract-ocr </dev/null >/dev/null
sed -i '/^mozilla\/DST_Root_CA_X3.crt$/ s/^/!/' /etc/ca-certificates.conf
update-ca-certificates

cd $APP_HOME
cp . ./
chmod +x /app/_install/post_install.sh
chmod +x /app/_install/install_tessy.sh
/app/_install/post_install.sh
/app/_install/install_tessy.sh
# clean up install scripts
# rm -rf /app/_install/post_install.sh
#gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 app:app
