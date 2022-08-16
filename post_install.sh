python3 -m pip install --quiet --no-cache-dir -r Requirements.txt
cd $VUE_HOME
npm install  && npm run build
mkdir $TESSERACT_DATA_FAST_INSTALL_FOLDER
cd $TESSERACT_DATA_FAST_INSTALL_FOLDER
git clone https://github.com/tesseract-ocr/tessdata_fast.git < /dev/null > /dev/null

