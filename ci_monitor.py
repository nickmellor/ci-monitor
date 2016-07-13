from time import sleep
import sys
import datetime

import schedule

from conf import o_conf, config_changed
from indicator import Indicator
from utils.logger import logger, configure_logging


def setup():
    global first_time, last_day
    message = 'CI Monitor '
    message += 'starting for the first time' if first_time else 'restarted'
    if first_time:
        first_time = False
    logger.warning(message)
    configure_logging()
    logger.info("Using configuration file ''")
    schedule.clear()
    for name, settings in o_conf().indicators.items():
        indicators.append(Indicator(name, settings))
    last_day = day_of_month()


def day_of_month():
    return datetime.datetime.now().day


def listen():
    global indicators
    for indicator in indicators:
        schedule.run_pending()
        try:
            indicator.run()
        except KeyboardInterrupt as e:
            logger.warning('Interrupted by Ctrl+C: exiting...')
            sys.exit()
        except Exception as e:
            logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
            sleep(o_conf().errorheartbeat_secs)
        else:
            # heartbeat avoids busy wait in monitoring app
            sleep(o_conf().heartbeat_secs)


first_time = True
indicators = []
while True:
    setup()
    while True:
        if config_changed():
            logger.warning('Config changed!')
            break
        today = day_of_month()
        if today != last_day:
            logger.info('Date flip-- restarting!')
            last_day = today
            break
        listen()


# TODO: catch internal exception: KeyError('successfulTestCount',)
# TODO: py2exe is broken-- can't do dynamic imports
# TODO: unit tests(!)
# TODO: test recovery from persistent error (e.g. build fixed)
# TODO: exclusions list for merges(?)
# TODO: check traffic light transitions
# TODO: factor out message building (esp. indicator name)
# TODO: log to info when polling listener (move to indicator)
# TODO: results dropped as JSON in directory (further decouple indications from results)
# TODO: consider multi-threading
