from time import sleep
import sys
import datetime

import schedule

from conf import o_conf, config_changed
from indicator import Indicator
from utils.logger import logger, configure_logging

def day_of_month():
    return datetime.datetime.now().day

last_day = day_of_month()

while True:
    logger.warning('CI Monitor restarted')
    configure_logging()
    schedule.clear()
    indicators = []
    for name, settings in o_conf().indicators.items():
        indicators.append(Indicator(name, settings))
    while True:
        if config_changed():
            logger.warning('Config changed!')
            break
        today = day_of_month()
        if today != last_day:
            logger.warning('Date flip-over!')
            last_day = today
            break
        for indicator in indicators:
            try:
                indicator.run()
            except KeyboardInterrupt as e:
                logger.warning('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
                sleep(o_conf().defaults.errorheartbeat_secs)
            else:
                sleep(o_conf().defaults.heartbeat_secs)



# TODO: unit tests(!)
# TODO: repeat suppressed "indications" daily (suppressed repeat errors)
# TODO: test recovery from persistent error (e.g. build fixed)
# TODO: exclusions list for merges(?)
# TODO: check traffic light transitions
# TODO: traffic light blink
# TODO: factor out message building (esp. indicator name)
# TODO: ScheduleSetter log to info when polling monitor (move from indicator)
# TODO: monitors return results as Python objects; indicator can output
# TODO: Detect and Show for Monitor and Indicator? But disallows detect to be an action not a test
# TODO: consider multi-threading
# TODO: find config and scratch automatically when running as .exe
