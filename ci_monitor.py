from time import sleep
from conf import configuration, o_conf, config_changed
import sys
from cimsignal import Signal
from logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    configure_logging()
    signals = []
    for signal_id in o_conf().signals:
        signals.append(Signal(signal_id))
    while not config_changed():
        unhandled_exceptions = []
        for signal in signals:
            try:
                signal.poll()
            except KeyboardInterrupt as e:
                logger.warning('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                unhandled_exceptions.append(signal.unhandled_exception_raised)
        if any(unhandled_exceptions):
            logger.error("Unhandled exception(s) in CI-Monitor:\n{0}".format(repr(unhandled_exceptions)))
            sleep(o_conf().errorheartbeat_secs)
        else:
            sleep(o_conf().heartbeat_secs)
    logger.warning('Config changed!')

# TODO: decouple signals so they operate independently-- separate threads?
# TODO: sep of concerns: monitors like Bamboo should expose methods for signal
#         - poll()
#         - state()
#         - comms()
# TODO: rename State to Persist
