from time import sleep

import soundplayer
from bamboo import Bamboo
from conf import configuration
from geckoboard import Geckoboard
from logger import logger
from state import State
from traffic import TrafficLight
from sitemap import Sitemap

states = configuration['states']


class Signal:
    """
    a signal associates builds/status of services with signals (traffic lights, sounds etc)
    a signal might read the API functional tests Bamboo build, play a sound if they have
    failing test(s), and display the build status on a traffic light
    or make a sound, or write to a log
    each signal has a 'state'-- that encompasses Bamboo responsiveness, test failures,
    presence of configured traffic lights, internal exceptions
    states are divided into ERROR, WARNING and NONE that are configurable, and currently
    affect the logging level
    """

    def __init__(self, signal_name):
        self.signal_name = signal_name
        self.state = self.get_state()
        self.signal_settings = configuration['signals'][signal_name]
        self.unhandled_exception_raised = False
        traffic_light_present = self.signal_settings.get('trafficlight')
        self.trafficlight = TrafficLight(signal_name, self.signal_settings['trafficlight']) if traffic_light_present else None
        self.sitemap = Sitemap(self.signal_settings['sitemap'], self.signal_name) if self.signal_settings.get('sitemap') else None
        self.bamboo_tasks = Bamboo(self.signal_settings['bamboo']) if self.signal_settings.get('bamboo') else None
        self.geckoboard = Geckoboard()

    def get_state(self):
        return State.retrieve(self.state_id())

    def state_id(self):
        return 'signal:{signal}'.format(signal=self.signal_name)

    def poll(self):
        logger.info('Signal {signal}: polling...'.format(signal=self.signal_name))
        try:
            bamboo_results = self.bamboo_tasks.all_results() if self.bamboo_tasks else None
            sitemap_ok = self.sitemap.urls_ok() if self.sitemap else True
        except Exception as e:
            logger.error('Signal {signal}: Unhandled internal exception. '
                         'Could be configuration problem or bug.\n{exception}'
                         .format(signal=self.signal_name, exception=e.args))
            self.internal_exception(e)
            # NB traffic light update not shown until unhandled exception clear for one complete pass
            logger.error('Waiting {0} secs\n'.format(configuration['errorheartbeat_secs']))
            sleep(configuration['errorheartbeat_secs'])
        else:
            self.communicate_results(bamboo_results, sitemap_ok)
            self.geckoboard.show_monitored_environments(bamboo_results)
            if self.unhandled_exception_raised:
                self.unhandled_exception_raised = False

    def signal_unhandled_exception(self, e):
        logger.error("Signal {signal}: internal exception occurred:\n{exception}".format(signal=self.signal_name, exception=e))
        self.unhandled_exception = True

    def respond_to_error_level(self, new_state):
        errors = states['lamperror']
        is_new_error = new_state in errors
        warnings = states['lampwarn']
        is_new_warning = new_state in warnings
        change_to_from_error = is_new_error != (self.get_state() in errors)
        change_to_from_warning = is_new_warning != (self.get_state() in warnings)
        change_of_error_level = change_to_from_error or change_to_from_warning
        if change_of_error_level:
            sound = self.signal_settings['sounds']
            if is_new_error or is_new_warning:
                wav = sound['failures']
            else:
                wav = sound['greenbuild']
            soundplayer.playwav(wav)
        if change_to_from_error:
            level = 'ERROR'
        elif change_to_from_warning:
            level = 'WARNING'
        else:
            level = 'NONE'
        message = "State changing from '{previous}' to '{current}'"\
            .format(previous=self.get_state(), current=new_state)
        logger_method = {'ERROR': logger.error,
                         'WARNING': logger.warn,
                         'NONE': logger.info}
        logger_method[level](message)
        if self.trafficlight:
            self.trafficlight.set_lights(new_state)

    def internal_exception(self, e):
        if not self.unhandled_exception_raised:
            self.signal_unhandled_exception(e)
            self.respond_to_error_level('internalexception')

    def communicate_results(self, bamboo_results, sitemap_ok):
        all_passed = True
        comms_failure = False
        if bamboo_results:
            for env_results in bamboo_results.values():
                project_results = env_results.values()
                retrieved_results = [result for result in project_results if result is not None]
                # all returns True for empty list
                all_passed = all_passed and all(retrieved_results)
                if all_passed:
                    all_passed = all_passed and all(retrieved_results)
                if any(passed is None for passed in project_results):
                    comms_failure = True
        else:
            all_passed = True
        all_passed = all_passed and sitemap_ok
        if comms_failure:
            if all_passed:
                state = 'commserror'
            else:
                state = 'commserrorandfailures'
        else:
            if all_passed:
                state = 'alltestspassed'
            else:
                state = 'failures'
        if self.get_state() != state:
            self.respond_to_error_level(state)
            self.store_signal_state(state)
        else:
            if self.trafficlight:
                self.trafficlight.set_lights(state)

    def store_signal_state(self, state):
        State.store(self.state_id(), state)


# TODO: BSM/New Relic
# TODO: Geckoboard
