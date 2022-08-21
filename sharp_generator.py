import os
import sys

from generic_helpers.generate_sharp import output_js_filename, _s
from app import api_generator

if __name__ == '__main__':
    if not os.path.exists(_s):
        os.makedirs(_s)

    api_generator.generate(output_js_filename)
    print("done")
    raise RuntimeError("Done")
    sys.exit(0)



