from time import sleep
import sys
import datetime

import schedule

from conf import o_conf, config_changed, config_filename
from indicator import Indicator
from utils.logger import logger, configure_logging

cold_start = True


def setup():
    global cold_start, day_stamp, indicators
    indicators = []
    message = ['CI Monitor']
    message.append('starting from cold' if cold_start else 'restarted')
    if cold_start:
        cold_start = False
    configure_logging()
    message.append("using configuration file '{0}'".format(config_filename()))
    logger.warning(' '.join(message))
    schedule.clear()
    for indicator_id, settings in o_conf().indicators.items():
        indicators.append(Indicator(indicator_id, settings))
    day_stamp = day_of_month()


def day_of_month():
    return datetime.datetime.now().day


def monitor():
    global indicators
    for indicator in indicators:
        schedule.run_pending()
        try:
            indicator.run()
        except KeyboardInterrupt as e:
            logger.warning('Interrupted by Ctrl+C: exiting...')
            sys.exit()
        except Exception as e:
            logger.error("Unhandled exception running indicator '{name}':\n"
                         "Exception as follows:\n"
                         "{exception}\n"
                         "Stacktrace:\n"
                         "{stacktrace}\n".format(name=indicator.indicator_name, exception=repr(e)), stacktrace="can't show stacktrace")
            indicator.signal_unhandled_exception(e)
            sleep(o_conf().errorheartbeat_secs)
        else:
            # avoid busy wait
            sleep(o_conf().heartbeat_secs)


while True:
    setup()
    while True:
        if config_changed():
            logger.warning('Config changed!')
            break
        today = day_of_month()
        if today != day_stamp:
            logger.info('Date flip-- restarting!')
            day_stamp = today
            break
        monitor()


# TODO: py2exe is broken-- can't do dynamic imports
# TODO: doubling up of traffic light log messages
# TODO: log level reconfigure is broken-- log level stays the same
# TODO: overlogging of traffic light device at info level
# TODO: unit tests(!)
# TODO: test recovery from persistent error (e.g. build fixed)
# TODO: exclusions list for merges(?)
# TODO: check traffic light transitions
# TODO: factor out message building (esp. indicator name)
# TODO: log to info when polling listener (move to indicator)
# TODO: results dropped as JSON in directory (further decouple indications from results)
# TODO: consider multi-threading
