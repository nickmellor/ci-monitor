from time import sleep
from conf import conf, reload_config
import sys
import bamboo
from signaller import Signaller
from logger import logger

logger.info('CI Monitor started')

signaller = Signaller('OMS')

while True:
    try:
        signaller.poll()
    except KeyboardInterrupt as e:
        logger.error('Interrupted by Ctrl+C: exiting...')
        sys.exit()
    else:
        if not signaller.unhandled_exception_raised():
            sleep(conf['heartbeat_secs'])
    oldconf = conf
    conf = reload_config()
    if oldconf != conf:
        logger.warning('Configuration file has changed. Reloaded config')

# TODO: BSM XML parsing and summarising
# TODO: enable one server to look after more than one Geckoboard widget
# TODO: decouple signals so they operate independently-- separate threads?
# TODO: geckoboard: display a few failing tests (+ most recent committers?)
# TODO: signaller does not attempt to use absent devices (traffic light, geckoboard etc)
