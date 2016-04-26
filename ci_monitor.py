from time import sleep
import conf
import sys
from signaller import Signaller
from logger import logger, configure_logging

logger.warning('CI Monitor restarted')
while True:
    while not conf.config_changed():
        unhandled_exceptions = []
        for signaller_id in conf.configuration['signallers']:
            signaller = Signaller(signaller_id)
            try:
                signaller.poll()
            except KeyboardInterrupt as e:
                logger.error('Interrupted by Ctrl+C: exiting...')
                sys.exit()
            except Exception as e:
                unhandled_exceptions.append(signaller.unhandled_exception_raised)
        if any(unhandled_exceptions):
            sleep(conf.configuration['errorheartbeat_secs'])
        else:
            sleep(conf.configuration['heartbeat_secs'])
    configure_logging()
    logger.warning('Config changed!')

# TODO: fix logging level when config changes (conf being shadowed locally?)
# TODO: enable one CI-monitor to look after more than one Geckoboard widget
# TODO: decouple signals so they operate independently-- separate threads?
# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: add last downtime facility for Geckoboard
# TODO: HipChat notification of build going red/green
