import os
import shutil

path_to_extensions = os.environ.get('EXTENSIONS_PATH')
shutil.copy2('rasterin.inx', path_to_extensions)
shutil.copy2('rasterin.py', path_to_extensions)
