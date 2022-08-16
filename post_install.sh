python3 -m pip install --upgrade pip
python3 -m pip install --quiet --no-cache-dir -r Requirements.txt
rm -rf static
unzip /app/front_end.zip -d /app/static
rm -rf /app/front_end /app/front_end.zip

