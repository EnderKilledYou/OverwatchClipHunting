
from sharp import Sharp, naming

from app import app


api_generator = Sharp(app, prefix="/api", naming=naming.file_based)


def get_sharp():
    return api_generator


