import os
import logging
from conf import conf
from logging.handlers import TimedRotatingFileHandler

loglevel_lookup = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'debug': logging.DEBUG,
    'info': logging.INFO
}

logging.captureWarnings(True)
logger = logging.getLogger('log')
logger.setLevel(loglevel_lookup[conf['logging']['level']])
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
filehandler = TimedRotatingFileHandler(when='H', interval=24,
                                       filename=os.path.join('logs', 'log'),
                                       backupCount=14, delay=True)
filehandler.setFormatter(formatter)
if conf['logging'].get('console'):
    conshandler = logging.StreamHandler()
    conshandler.setFormatter(formatter)
    logger.addHandler(conshandler)
logger.addHandler(filehandler)

