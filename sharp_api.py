from sharp import Sharp, naming

from app import app


def get_sharp():
    api_generator = Sharp(app, prefix="/api", naming=naming.file_based)
    return api_generator


def print_sharp():
    get_sharp().generate("src/js/sharp.gen.js")


sharp_api = get_sharp()
