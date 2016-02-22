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

# to keep PyCharm code inspection happy
logger = None


def configure_logging():
    logconf = conf['logging']
    logging.captureWarnings(True)
    global logger
    logger = logging.getLogger('log')
    logger.propagate = False
    formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
    if logconf['fileRotator']:
        filehandler = TimedRotatingFileHandler(when='H', interval=24,
                                               filename=os.path.join('logs', 'log'),
                                               backupCount=14, delay=True)
        filehandler.setLevel(loglevel_lookup[logconf['fileRotator']])
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    # NB console handler needs configuring after file handler
    # otherwise logger doubles messages
    if logconf['console']:
        conshandler = logging.StreamHandler()
        conshandler.setLevel(loglevel_lookup[logconf['console']])
        conshandler.setFormatter(formatter)
        logger.addHandler(conshandler)


configure_logging()
