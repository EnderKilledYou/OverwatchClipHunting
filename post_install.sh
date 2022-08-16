python3 -m pip install --upgrade pip
python3 -m pip install --quiet --no-cache-dir -r Requirements.txt
cd $VUE_HOME
npm install  && npm run build
rm -rf node_modules
#mkdir $TESSERACT_DATA_FAST_INSTALL_FOLDER
#cd $TESSERACT_DATA_FAST_INSTALL_FOLDER
#git clone --quiet https://github.com/tesseract-ocr/tessdata_fast.git < /dev/null > /dev/null

