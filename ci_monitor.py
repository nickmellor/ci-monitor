from time import sleep
import datetime
import bamboo
from traffic import TrafficLight
from geckoboard import Geckoboard

traffic_light_environments = ['SIT']
geckoboard_environments = ['SIT']
HEARTBEAT_SECONDS = 30

our_first_traffic_light = TrafficLight(monitored_environments=traffic_light_environments)
our_first_geckoboard = Geckoboard(monitored_environments=geckoboard_environments)

while True:
    try:
        print('Timestamp: {0}'.format(datetime.datetime.now()))
        results = bamboo.collect_bamboo_data()
        our_first_traffic_light.show_results(results)
        our_first_geckoboard.show_results(results)
        our_first_traffic_light.clear_unhandled_exception()
    except Exception as e:
        print('Unhandled exception. Check proxy connection?\n{0}'.format(e))
        our_first_traffic_light.big_trouble()
        our_first_traffic_light.signal_unhandled_exception()
        # NB traffic light update not shown until unhandled exception clear for one complete pass
    sleep(HEARTBEAT_SECONDS)

# TODO: factor out common code between Bamboo and BSM requests
# TODO: YAML config
# TODO: BSM XML parsing and summarising
# TODO: git on Raspberry Pi, SSL to Raspberry Pi
# TODO: git repo public
# TODO: improve Raspberry Pi security-- don't login as root