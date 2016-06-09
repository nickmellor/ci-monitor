from time import sleep
import sys

import schedule

from conf import o_conf, config_changed
from indicator import Indicator
from utils.logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    configure_logging()
    schedule.clear()
    indicators = []
    for name, settings in o_conf().indicators.items():
        indicators.append(Indicator(name, settings))
    while not config_changed():
        for indicator in indicators:
            # try:
                indicator.run()
            # except KeyboardInterrupt as e:
            #     logger.warning('Interrupted by Ctrl+C: exiting...')
            #     sys.exit()
            # except Exception as e:
            #     logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
            #     sleep(o_conf().defaults.errorheartbeat_secs)
            # else:
                sleep(o_conf().defaults.heartbeat_secs)
    logger.warning('Config changed!')

# TODO: unit tests
# TODO: consider making merge atomic. Leads to repetitive config but reduces code exceptions and long delays
# TODO: deal with unhandled exceptions in new architecture
# TODO: check traffic light transitions in new architecture
# TODO: traffic light blink (indicator) in new architecture
# TODO: unhandled exceptions in indicators
# TODO: factor out message building (esp. indicator name)
# TODO: ScheduleSetter log to info when polling monitor (move from indicator)
# TODO: monitors return results as Python objects; indicator can output
# TODO: Detect and Show for Monitor and Indicator? But disallows detect to be an action not a test
# TODO: consider multi-threading
# TODO: find config and scratch automatically when running as .exe
