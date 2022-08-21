export TESSERACT_DATA_FAST_INSTALL_FOLDER=/FAST_DATA
export TESSERACT_DATA_FAST=/FAST_DATA/tessdata_fast/
git pull
sudo TESSERACT_DATA_FAST=/FAST_DATA/tessdata_fast/ gunicorn --bind :80 --workers 1 --threads 8 --timeout 0 app:app  > log.txt 2>&1
