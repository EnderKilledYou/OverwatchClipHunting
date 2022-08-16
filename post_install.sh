python3 -m pip install --upgrade pip
python3 -m pip install --quiet --no-cache-dir -r Requirements.txt
rm -rf static
unzip front_end.zip static
rm -rf front_end front_end.zip

