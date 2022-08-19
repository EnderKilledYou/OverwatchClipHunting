import os
from config.config import tess_fast_dir


def install():
    if not os.path.exists(tess_fast_dir):
        if 'INSTALL_SCRIPT' in os.environ:
            print("--------------Installing Tesseract---------------")
            os.system(os.environ['INSTALL_SCRIPT'])


