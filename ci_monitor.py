from time import sleep
from conf import conf, config_changed
import sys
from signaller import Signaller
from logger import logger

logger.info('CI Monitor started')
while True:
    while not config_changed():
        signaller = Signaller('OMS')
        try:
            signaller.poll()
        except KeyboardInterrupt as e:
            logger.error('Interrupted by Ctrl+C: exiting...')
            sys.exit()
        else:
            if not signaller.unhandled_exception_raised():
                sleep(conf['heartbeat_secs'])

# TODO: fix coming off warning/error-- currently not logging
# TODO: BSM XML parsing and summarising
# TODO: enable one server to look after more than one Geckoboard widget
# TODO: decouple signals so they operate independently-- separate threads?
# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: add last downtime facility for Geckoboard
# TODO: HipChat notification of build going red/green
