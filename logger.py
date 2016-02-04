import os
import logging
from logging.handlers import TimedRotatingFileHandler

logging.captureWarnings(True)
logger = logging.getLogger('log')
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
handler = TimedRotatingFileHandler(when='H', interval=24,
                                   filename=os.path.join('logs', 'log'),
                                   backupCount=14, delay=True)
handler.setFormatter(formatter)
logger.addHandler(handler)

