import logging
from logging.handlers import TimedRotatingFileHandler

logger = logging.Logger('log')
logger.setLevel(logging.WARNING)
formatter = logging.Formatter('%(asctime)s:%(levelname)s: %(message)s')
handler = TimedRotatingFileHandler(when='D', interval=1, filename='logs/log', backupCount=14, delay=True)
handler.setFormatter(formatter)
logger.addHandler(handler)

