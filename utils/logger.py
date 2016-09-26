import logging
import os
from logging.handlers import TimedRotatingFileHandler

from conf import raw_conf

loglevel_lookup = {
    'error': logging.ERROR,
    'warning': logging.WARNING,
    'debug': logging.DEBUG,
    'info': logging.INFO
}

logging.captureWarnings(True)
logger = logging.getLogger('log')
logger.setLevel(logging.INFO)
logger.propagate = True
cons_handler = None
file_handler = None


def configure_logging():
    global logger, cons_handler, file_handler
    logconf = raw_conf()['logging']
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    if logger.hasHandlers():
        logger.removeHandler(cons_handler)
        cons_handler = None
        logger.removeHandler(file_handler)
        file_handler = None
        print("should be empty: {0}".format(logger.handlers))
    file_loglevel = logconf['fileRotator']
    if file_loglevel:
        file_handler = TimedRotatingFileHandler(when='H', interval=24,
                                               filename=os.path.join('logs', 'log'),
                                               backupCount=14, delay=True)
        file_handler.setLevel(loglevel_lookup[file_loglevel])
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    # NB console handler needs configuring after file handler
    # otherwise logger doubles messages
    console_loglevel = logconf['console']
    if console_loglevel:
        cons_handler = logging.StreamHandler()
        cons_handler.setLevel(loglevel_lookup[console_loglevel])
        cons_handler.setFormatter(formatter)
        logger.addHandler(cons_handler)