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
            try:
                indicator.run()
            except KeyboardInterrupt as e:
                logger.warning('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
                sleep(o_conf().errorheartbeat_secs)
            else:
                sleep(o_conf().defaults.heartbeat_secs)
    logger.warning('Config changed!')

# TODO: state collation in indicators
# TODO: deal with unhandled exceptions in new architecture
# TODO: sep of concerns: monitors like Bamboo should expose methods for indicator
# TODO: implement scheduling
# TODO: traffic light transitions in new architecture
#         - poll()
#         - state() -- or should this be in indicator?
#         - comms()
