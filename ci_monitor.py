from time import sleep
from conf import conf, config_changed
import sys
from signaller import Signaller
from logger import logger
from conf import config_changed

logger.info('CI Monitor started')
while True:
    signaller = Signaller('OMS')
    while not config_changed():
        try:
            signaller.poll()
        except KeyboardInterrupt as e:
            logger.error('Interrupted by Ctrl+C: exiting...')
            sys.exit()
        else:
            if not signaller.unhandled_exception_raised():
                sleep(conf['heartbeat_secs'])


# TODO: BSM XML parsing and summarising
# TODO: enable one server to look after more than one Geckoboard widget
# TODO: decouple signals so they operate independently-- separate threads?
# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: add last downtime facility for Geckoboard
# TODO: classize bamboo module
# TODO: signaller does not attempt to use absent devices (traffic light, geckoboard etc)
# TODO: Hipchat notification of build going red/green
