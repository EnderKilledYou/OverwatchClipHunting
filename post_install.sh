python3 -m pip install --upgrade pip
python3 -m pip install --quiet --no-cache-dir -r Requirements.txt
cd $VUE_HOME
npm install  && npm run build
rm -rf node_modules


