from time import sleep

import soundplayer
from bamboo import Bamboo
from conf import conf
from geckoboard import Geckoboard
from logger import logger
from state import State
from traffic import TrafficLight

traffic_light_settings = conf['trafficlights']

class Signaller:
    """
    has a concept of 'state'-- Bamboo responsiveness, test failures, exceptions are examples
    connects builds/status of services with methods of signalling (traffic lights, sounds)
    """

    def __init__(self, signal_name):
        self.signal_name = signal_name
        self.state = self.get_state()
        self.signal_settings = conf['signallers'][signal_name]
        self.unhandled_exception = False
        self.trafficlight = TrafficLight(signal_name, self.signal_settings['trafficlight'])
        self.bamboo_tasks = Bamboo(self.signal_settings['bamboo'])
        self.geckoboard = Geckoboard()

    def get_state(self):
        return State.retrieve(self.state_id())

    def state_id(self):
        return 'signaller:{signal}'.format(signal=self.signal_name)

    def poll(self):
        logger.info('Signaller {signaller}: polling...'.format(signaller=self.signal_name))
        try:
            results = self.bamboo_tasks.all_results()
        except Exception as e:
            logger.error('Signaller {signaller}: Unhandled internal exception. '
                         'Could be configuration problem or bug.\n{exception}'
                         .format(signaller=self.signal_name, exception=e.args))
            self.internal_exception(e)
            # NB traffic light update not shown until unhandled exception clear for one complete pass
            logger.error('Waiting {0} secs\n'.format(conf['errorheartbeat_secs']))
            sleep(conf['errorheartbeat_secs'])
        else:
            self.show_results(results)
            self.geckoboard.show_monitored_environments(results)
            if self.unhandled_exception_raised():
                self.clear_unhandled_exception()

    def unhandled_exception_raised(self):
        return self.unhandled_exception

    def signal_unhandled_exception(self, e):
        logger.error("Signal {signal}: internal exception occurred:\n{exception}".format(signal=self.signal_name))
        self.unhandled_exception = True

    def clear_unhandled_exception(self):
        logger.warning("Signal {signal}: internal exception cleared".format(signal=self.signal_name))
        self.unhandled_exception = False

    def respond_to_error_level(self, new_state):
        errors = traffic_light_settings['lamperror']
        is_new_error = new_state in errors
        warnings = traffic_light_settings['lampwarn']
        is_new_warning = new_state in warnings
        change_to_from_error = is_new_error != (self.get_state() in errors)
        change_to_from_warning = is_new_warning != (self.get_state() in warnings)
        change_of_error_level = change_to_from_error or change_to_from_warning
        if change_of_error_level:
            sound = self.signal_settings['sounds']
            if is_new_error or is_new_warning:
                wav = sound['fail']
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
        self.trafficlight.set_lights(new_state)

    def internal_exception(self, e):
        if not self.unhandled_exception_raised():
            self.signal_unhandled_exception(e)
            self.respond_to_error_level('internalexception')

    def show_results(self, bamboo_results):
        all_passed = True
        comms_failure = False
        for env_results in bamboo_results.values():
            project_results = env_results.values()
            retrieved_results = [result for result in project_results if result is not None]
            # all returns True for empty list
            all_passed = all_passed and retrieved_results is not None
            all_passed = all_passed and all(retrieved_results)
            if any(passed is None for passed in project_results):
                comms_failure = True
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
            self.store_state(state)
        else:
            self.trafficlight.set_lights(state)

    def store_state(self, state):
        State.store(self.state_id(), state)
