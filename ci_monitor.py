from time import sleep
from conf import configuration, o_conf, config_changed
import sys
from indicator import Indicator
from logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    configure_logging()
    indicators = []
    for indicator_id in o_conf().indicators:
        indicators.append(Indicator(indicator_id))
    while not config_changed():
        for ind in indicators:
            try:
                ind.run()
            except KeyboardInterrupt as e:
                logger.warning('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(e)))
                sleep(o_conf().errorheartbeat_secs)
        else:
            sleep(o_conf().heartbeat_secs)
    logger.warning('Config changed!')

# TODO: decouple indicators so they operate independently-- separate threads?
# TODO: sep of concerns: monitors like Bamboo should expose methods for signal
#         - poll()
#         - state() -- or should this be in indicator?
#         - comms()
