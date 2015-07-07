import os
import logging
from conf import conf
from logging.handlers import TimedRotatingFileHandler

logger = logging.getLogger('loggingIsNotWorking')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
rc = conf['logs']['rotator']
handler = TimedRotatingFileHandler(when=rc['when'], interval=rc['interval'],
                                   filename=os.path.join(rc['logdir'], rc['logfile']),
                                   backupCount=rc['backupcount'], delay=True)
handler.setFormatter(formatter)
logger.addHandler(handler)

