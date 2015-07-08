import os
import logging
from conf import conf
from logging.handlers import TimedRotatingFileHandler

logging.captureWarnings(True)
logger = logging.getLogger('log')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
handler = TimedRotatingFileHandler(when='M', interval=10,
                                   filename=os.path.join('logs', 'log'),
                                   backupCount=14, delay=True)
handler.setFormatter(formatter)
logger.addHandler(handler)

