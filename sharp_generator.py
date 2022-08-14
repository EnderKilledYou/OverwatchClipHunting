import os
from app import app
from generate_sharp import output_js_filename, _s
from sharp_api import api_generator

if __name__ == '__main__':
    if not os.path.exists(_s):
        os.makedirs(_s)

    api_generator.generate(output_js_filename)



