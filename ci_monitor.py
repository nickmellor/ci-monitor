from time import sleep
from conf import configuration, o_conf, config_changed
import sys
from signaller import Signaller
from logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    while not config_changed():
        unhandled_exceptions = []
        for signaller_id in o_conf().signallers:
            signaller = Signaller(signaller_id)
            try:
                signaller.poll()
            except KeyboardInterrupt as e:
                logger.warning('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                unhandled_exceptions.append(signaller.unhandled_exception_raised)
        if any(unhandled_exceptions):
            sleep(o_conf().errorheartbeat_secs)
        else:
            sleep(o_conf().heartbeat_secs)
    configure_logging()
    logger.warning('Config changed!')

# TODO: fix logging level when config changes (conf being shadowed locally?)
# TODO: enable one CI-monitor to look after more than one Geckoboard widget
# TODO: decouple signals so they operate independently-- separate threads?
# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: add last downtime facility for Geckoboard
# TODO: HipChat notification of build going red/green
