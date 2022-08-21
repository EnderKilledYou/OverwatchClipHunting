import os

from app import app

os.environ['OCR_PRODUCTION'] = True
os.environ['DB_USER'] = True
os.environ['DB_SECRET'] = True
os.environ['DB_NAME'] = True
os.environ['DB_HOST'] = True
if __name__ == '__main__':
    app.run(threaded=True)

# waitress(app)
