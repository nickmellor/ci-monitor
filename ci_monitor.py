from time import sleep

import schedule

from conf import o_conf, config_changed
from indicator import Indicator
from utils.logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    configure_logging()
    indicators = []
    for name, settings in o_conf().indicators.items():
        indicators.append(Indicator(name, settings))
    while not config_changed():
        schedule.clear()
        for indicator in indicators:
            # try:
            indicator.run()
            # except KeyboardInterrupt as e:
            #     logger.warning('Interrupted by Ctrl+C: exiting...')
            #     sys.exit()
            # except Exception as e:
            #     logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
            #     sleep(o_conf().errorheartbeat_secs)
            # else:
            sleep(o_conf().defaults.schedule.heartbeat_secs)
    logger.warning('Config changed!')

# TODO: decouple indicators so they operate independently-- separate threads?
# TODO: sep of concerns: monitors like Bamboo should expose methods for indicator
#         - poll()
#         - state() -- or should this be in indicator?
#         - comms()
