import colorlog
import logging
import sys
import os

_handler = logging.StreamHandler()
_handler.setFormatter(colorlog.ColoredFormatter('%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s'))

def getLogger():
    logger = logging.getLogger(os.path.basename(sys.argv[0]))
    logger.addHandler(_handler)
    logger.setLevel(logging.DEBUG)
    return logger
