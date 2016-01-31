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
    has a concept of 'state'-- Bamboo responsiveness, exceptions etc
    connects builds/status of services with methods of signalling (traffic lights, sounds)
    """

    def __init__(self, signal_name):
        self.signal_name = signal_name
        self.state = State.retrieve(self.state_id())
        self.signal_settings = conf['signallers'][signal_name]
        self.unhandled_exception = False
        self.trafficlight = TrafficLight(signal_name, self.signal_settings['trafficlight'])
        self.bamboo_tasks = Bamboo(self.signal_settings['bamboo'])
        self.geckoboard = Geckoboard()

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
            self.internal_exception()
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

    def signal_unhandled_exception(self):
        self.unhandled_exception = True

    def clear_unhandled_exception(self):
        logger.warning("Signal {signal}: internal exception cleared".format(signal=self.signal_name))
        self.unhandled_exception = False

    def respond_to_error_level(self, new_state):
        errors = traffic_light_settings['lamperror']
        new_error = new_state in errors
        warnings = traffic_light_settings['lampwarn']
        new_warning = new_state in warnings
        change_to_from_error = new_error != (self.state in errors)
        change_to_from_warning = new_warning != (self.state in warnings)
        if change_to_from_error or change_to_from_warning:
            sound = self.signal_settings['sounds']
            if new_error or new_warning:
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
        message = "State changing from '{old}' to '{new}'".format(old=self.state, new=new_state)
        logger_method = {'ERROR': logger.error,
                         'WARNING': logger.warn,
                         'NONE': logger.info}
        logger_method[level](message)
        self.trafficlight.set_lights(new_state)

    def internal_exception(self):
        if not self.unhandled_exception_raised():
            self.signal_unhandled_exception()
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
        if self.state != state:
            self.respond_to_error_level(state)
            State.store(self.state_id(), state)
        else:
            self.trafficlight.set_lights(state)
