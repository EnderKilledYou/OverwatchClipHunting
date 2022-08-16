printenv
cd $VUE_HOME
npm install && npm run build
mkdir $TESSERACT_DATA_FAST_INSTALL_FOLDER
cd $TESSERACT_DATA_FAST_INSTALL_FOLDER
git clone https://github.com/tesseract-ocr/tessdata_fast.git
echo "installed"
