export TESSERACT_DATA_FAST_INSTALL_FOLDER=/FAST_DATA
export TESSERACT_DATA_FAST=/FAST_DATA/tessdata_fast/
mkdir $TESSERACT_DATA_FAST_INSTALL_FOLDER
cd $TESSERACT_DATA_FAST_INSTALL_FOLDER
git clone https://github.com/tesseract-ocr/tessdata_fast.git
rm -rf $INSTALL_SCRIPT