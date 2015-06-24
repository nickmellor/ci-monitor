from time import sleep
import warnings
import sys
import bamboo
from traffic import TrafficLight
from geckoboard import Geckoboard

from logger import logger

# show warnings first time (e.g. security certificate) then suppress
warnings.simplefilter('default', Warning)

logger.info('Started')

traffic_light_environments = ['SIT']
geckoboard_environments = ['SIT']
HEARTBEAT_SECONDS = 30

our_first_traffic_light = TrafficLight(monitored_environments=traffic_light_environments)
our_first_geckoboard = Geckoboard(monitored_environments=geckoboard_environments)

while True:
    try:
        logger.info('Polling')
        results = bamboo.collect_bamboo_data()
        our_first_traffic_light.show_results(results)
        our_first_geckoboard.show_results(results)
        our_first_traffic_light.clear_unhandled_exception()
        sleep(HEARTBEAT_SECONDS)
    except KeyboardInterrupt as e:
        logger.error('Interrupted by Ctrl+C: exiting...')
        sys.exit()
    except Exception as e:
        logger.error('Unhandled exception. Check proxy connection?\n{0}'.format(e))
        our_first_traffic_light.big_trouble()
        our_first_traffic_light.signal_unhandled_exception()
        # NB traffic light update not shown until unhandled exception clear for one complete pass

# TODO: factor out common code between Bamboo and BSM requests
# TODO: YAML config
# TODO: BSM XML parsing and summarising
# TODO: git on Raspberry Pi, SSL to Raspberry Pi
# TODO: git repo public
# TODO: improve Raspberry Pi security-- don't login as root