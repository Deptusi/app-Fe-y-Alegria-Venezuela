from kivy.utils import get_color_from_hex
__colorsH__=['#002C77','#FFFFFF','#00968F','#009DE0']
__colors__=[get_color_from_hex(color) for color in __colorsH__]


import os, logging
__defaultFolderPicker__=os.getcwd()
__defaultSaveLocation__=os.path.join(os.getcwd(),'Resultados')

from supportFiles.privateLogger import privateLogger
logging.root.setLevel(logging.NOTSET)
logger=privateLogger()
logger.setLevel(10)