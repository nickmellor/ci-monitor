import logging
from conf import conf
from logging.handlers import TimedRotatingFileHandler

logger = logging.Logger('log')
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
rc = conf['logs']['rotator']
handler = TimedRotatingFileHandler(when=rc['when'],
                                   interval=rc['interval'],
                                   filename=rc['logfile'],
                                   backupCount=rc['backupcount'], delay=True)
handler.setFormatter(formatter)
logger.addHandler(handler)

