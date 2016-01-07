from time import sleep
from conf import conf, reload_config
import sys
import bamboo
from signaller import Signaller
from geckoboard import Geckoboard
from logger import logger

logger.info('CI Monitor started')

traffic_light = Signaller('OMS')
geckoboard = Geckoboard()

while True:
    try:
        logger.info('Polling')
        results = bamboo.collect_bamboo_data()
        traffic_light.show_results(results)
        geckoboard.show_monitored_environments(results)
        traffic_light.clear_unhandled_exception()
        sleep(conf['heartbeat_secs'])
    except KeyboardInterrupt as e:
        logger.error('Interrupted by Ctrl+C: exiting...')
        sys.exit()
    except Exception as e:
        logger.error('Unhandled internal exception. Could be configuration problem or bug.\n{0}'.format(e))
        traffic_light.internal_exception()
        traffic_light.signal_unhandled_exception()
        # NB traffic light update not shown until unhandled exception clear for one complete pass
        logger.error('Waiting {0} secs\n'.format(conf['errorheartbeat_secs']))
        sleep(conf['errorheartbeat_secs'])
    oldconf = conf
    conf = reload_config()
    if oldconf != conf:
        logger.warning('Configuration file has changed. Reloaded config')
    logger.info('thump')

# TODO: factor out common code between Bamboo and BSM requests
# TODO: BSM XML parsing and summarising
# TODO: enable one server to look after more than one Geckoboard widget
# TODO: geckoboard
