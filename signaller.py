from time import sleep
from requests.exceptions import RequestException
from geckoboard import Geckoboard

import soundplayer
from logger import logger
from conf import conf
from traffic import TrafficLight
import bamboo

traffic_light_settings = conf['trafficlights']

class Signaller:
    """
    couples Bamboo builds to methods of signalling (traffic lights, sounds)
    """

    def __init__(self, signal_name):
        self.old_state = None
        self.signal_name = signal_name
        self.signal_settings = conf['signallers'][signal_name]
        self.environments = self.signal_settings['environments']
        logger.info("'{signaller}' signal is monitoring environments '{environments}'".format(
            signaller=signal_name, environments=', '.join(self.environments)))
        self.unhandled_exception = False
        self.trafficlight = TrafficLight(signal_name, self.signal_settings['trafficlightid'])
        self.bamboo_results = None
        self.geckoboard = Geckoboard()

    def poll(self):
        logger.info('Signaller {signaller}: polling...')
        try:
            results = bamboo.collect_bamboo_data()
        except RequestException as e:
            logger.error("Signaller {signaller}: can't get info from Bamboo:\n{exception}".format(signaller=self.signal_name, exception=e))
        except Exception as e:
            logger.error('Signaller {signaller}: Unhandled internal exception. Could be configuration problem or bug.\n{exception}'
                         .format(signaller=self.signal_name, exception=e.args))
            self.internal_exception()
            # NB traffic light update not shown until unhandled exception clear for one complete pass
            logger.error('Waiting {0} secs\n'.format(conf['errorheartbeat_secs']))
            sleep(conf['errorheartbeat_secs'])
        else:
            self.show_results(results)
            self.geckoboard.show_monitored_environments(results)
            self.clear_unhandled_exception()

    def unhandled_exception_raised(self):
        return self.unhandled_exception

    def signal_unhandled_exception(self):
        self.unhandled_exception = True

    def clear_unhandled_exception(self):
        logger.warning("Signal {signal}: internal exception cleared".format(signal=self.signal_name))
        self.unhandled_exception = False

    # def change_lights(self, new_state):
    #     # ignore requests to change lights if last run had an unhandled exception
    #     # (wait for stable recovery)
    #     if not self.unhandled_exception:
    #         if new_state != self.old_state:
    #             self.state_change(new_state)
    #             self.old_state = new_state

    def state_change(self, new_state):
        errors = traffic_light_settings['lamperror']
        new_error = new_state in errors
        warnings = traffic_light_settings['lampwarn']
        new_warning = new_state in warnings
        change_to_from_error = (new_error) != (self.old_state in errors)
        change_to_from_warning = (new_warning) != (self.old_state in warnings)
        if change_to_from_error:
            level = 'ERROR'
        elif change_to_from_warning:
            level = 'WARNING'
        else:
            level = 'NONE'
        self.trafficlight.change_lights(new_state, self.old_state, level)
        sound = self.signal_settings['sounds']
        if new_state in errors or new_state in warnings:
            wav = sound['fail']
        else:
            wav = sound['greenbuild']
        soundplayer.playwav(wav)
        self.old_state = new_state



    def internal_exception(self):
        self.signal_unhandled_exception()
        self.state_change('internalexception')

    # TODO: internal exceptions are not signal-specific

    def show_results(self, results):
        all_passed = True
        comms_failure = False
        for env in self.environments:
            env_results = results[env].values()
            all_passed = all_passed and all(env_results)
            if any(passed is None for passed in env_results):
                comms_failure = True
        state = 'allpassed' if all_passed else "commserror" if comms_failure else "failures"
        state = 'commserrorandfailures' if comms_failure and not all_passed else state
        if state != self.old_state:
            self.state_change(state)
        else:
            # TODO: move to traffic light class. TL needs to remember last setting
            self.trafficlight.blink()
            self.trafficlight.set_lights(self.old_state)
