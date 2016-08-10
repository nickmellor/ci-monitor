from functools import partial

from devices.traffic import TrafficLight

from utils import soundplayer
from conf import raw_conf, o_conf
from utils.logger import logger
from utils.getclass import get_class
from utils.schedulesetter import ScheduleSetter

states = raw_conf()['states']


class Indicator:
    """
    an indicator associates builds/status of services with indicators (traffic lights, sounds etc)
    an indicator might for example:

      - read the API functional tests Bamboo build, play a sound if they have
        failing test(s), and display the build status on a traffic light
      - make a sound and write to a log if a service is down

    each indicator has a 'state'-- that encompasses Bamboo responsiveness, test failures,
    presence of configured traffic lights, internal exceptions
    states are divided into ERROR, WARNING and NONE that are configurable, and currently
    affect the logging level
    """

    def __init__(self, indicator_name, settings):
        self.indicator_name = indicator_name
        self.state = None
        self.settings = settings
        self.unhandled_exception_raised_previously = False
        self.listeners = []
        self.setup_listeners()
        self.setup_devices()

    def setup_listeners(self):
        for listener_config in self.settings['listeners']:
            for listener_type, settings in listener_config.items():
                listener = self.schedule_listener(listener_type, settings, self.find_schedule(settings))
                self.listeners.append(listener)

    def schedule_listener(self, name, settings, schedule_location):
        try:
            class_name = 'listeners.{0}.{1}'.format(name, name.capitalize())
            listener = get_class(class_name)(self.indicator_name, name, settings)
            wrapped_listener = partial(self.run_wrapper, listener)
            ScheduleSetter(job=wrapped_listener, schedule_settings=schedule_location)
            return listener
        except NameError as e:
            message = "{indicator}: implementation for listener type '{listener}' " \
                      "is not available or incomplete\n" \
                      "Exception: {exception}\n"
            message = message.format(indicator=self.indicator_name, listener=name, exception=e)
            logger.error(message)

    def find_schedule(self, listener_settings):
        if listener_settings.get('schedule'):
            return listener_settings
        elif self.settings.get('schedule'):
            return self.settings
        else:
            return o_conf()

    def run_wrapper(self, listener):
        logger.info("Running indicator {indicator}, listener {clazz}:{listener} ...".format(indicator=listener.indicator_name,
            listener=listener.name, clazz=listener.listener_class))
        try:
            listener.poll()
        except Exception as e:
            logger.error('{indicator}: {listener}: unhandled exception as follows:\n{exception}'
                .format(indicator=listener.indicator_name, listener=listener.name, exception=repr(e)))

    def setup_devices(self):
        settings = self.settings['trafficlight']
        if settings:
            self.trafficlight = TrafficLight(self.indicator_name, settings)

    def run(self):
        state = self.get_state()
        self.show_change(state)
        if self.trafficlight:
            self.trafficlight.set_lights(state)
        self.state = state


        # except Exception as e:
        #     logger.error('Signal {signal}: Unhandled internal exception. '
        #                  'Could be configuration problem or bug.\n{exception}'
        #                  .format(signal=self.indicator_name, exception=e.args))
        #     self.internal_exception(e)
            # NB traffic light update not shown until unhandled exception clear for one complete pass
            # logger.error('Waiting {0} secs\n'.format(configuration['errorheartbeat_secs']))
            # sleep(configuration['errorheartbeat_secs'])

    def get_state(self):
        # for listener in self.listeners:
            # logger.info("{indicator}: polling '{name}' tests"
            #             .format(indicator=self.indicator_name, name=listener.name))
            # logger.info("  {0}:{1}:{2}".format(listener.tests_ok(), listener.comms_ok(), listener.has_changed()))
        comms_failures = any(not listener.comms_ok() for listener in self.listeners)
        test_failures = any(not listener.tests_ok() for listener in self.listeners)
        state = 1 if test_failures else 0
        state += 2 if comms_failures else 0
        return o_conf().states[state]

    def signal_unhandled_exception(self, e):
        logger.error("Indicator {indicator}: "
                     "internal exception occurred:\nException as follows:\n{exception}"
                     .format(indicator=self.indicator_name, exception=e))
        if not self.unhandled_exception_raised_previously:
            self.show_change('internalexception')
        self.unhandled_exception_raised_previously = True

    def show_change(self, state):
        severities = o_conf().severities
        errors = severities['errors']
        is_error = state in errors
        warnings = severities['warnings']
        is_warning = state in warnings
        change_to_from_error = is_error != (self.state in errors)
        change_to_from_warning = is_warning != (self.state in warnings)
        change_of_error_level = change_to_from_error or change_to_from_warning
        self.show_by_traffic_light(state)
        self.show_by_sound(change_of_error_level, is_error, is_warning)
        self.show_by_logging(change_to_from_error, change_to_from_warning, state)

    def show_by_traffic_light(self, state):
        state_changed = state != self.state
        if state_changed:
            self.trafficlight.state_change()
        else:
            self.trafficlight.blink()
        self.trafficlight.set_lights(state)

    def show_by_sound(self, change_of_error_level, is_error, is_warning):
        if change_of_error_level:
            sound = self.settings['sounds']
            if is_error or is_warning:
                wav = sound['failures']
            else:
                wav = sound['greenbuild']
            soundplayer.playwav(wav)

    def show_by_logging(self, change_to_from_error, change_to_from_warning, state):
        if change_to_from_error:
            level = 'ERROR'
        elif change_to_from_warning:
            level = 'WARNING'
        else:
            level = 'NONE'
        if not self.state and state != self.state:
            message = "State changing from '{previous}' to '{current}'" \
                .format(previous=self.state, current=state)
            logger_method = {'ERROR': logger.error,
                             'WARNING': logger.warn,
                             'NONE': logger.info}
            logger_method[level](message)
