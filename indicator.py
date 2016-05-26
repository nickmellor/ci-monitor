from time import sleep

# from monitors.bamboo import Bamboo
# from monitors.merge import Merge
# from monitors.sitemap import Sitemap
from utils import soundplayer
from conf import configuration, o_conf
from utils.logger import logger
from utils.persist import Persist
from utils.getclass import get_class
from utils.schedulesetter import ScheduleSetter

states = configuration['states']


class Indicator:
    """
    an indicator associates builds/status of services with signals (traffic lights, sounds etc)
    an indicator might

    - read the API functional tests Bamboo build, play a sound if they have
      failing test(s), and display the build status on a traffic light
    - make a sound and write to a log if a service is down

    each signal has a 'state'-- that encompasses Bamboo responsiveness, test failures,
    presence of configured traffic lights, internal exceptions
    states are divided into ERROR, WARNING and NONE that are configurable, and currently
    affect the logging level
    """

    def __init__(self, indicator_name, settings):
        self.indicator_name = indicator_name
        # self.state = self.get_state()
        self.state = None
        self.settings = settings
        self.unhandled_exception_raised = False
        self.monitors = []
        for monitor_config in self.settings.monitoring:
            for monitor_name, monitor_settings in monitor_config.items():
                monitor = self.initalise_monitor(monitor_name,
                                            monitor_settings, self.find_schedule(monitor_settings))
                self.monitors.append(monitor)

    def initalise_monitor(self, monitor_name, monitor_settings, schedule_location):
        try:
            monitor_class = 'monitors.{0}.{1}'.format(monitor_name, monitor_name.capitalize())
            monitor = get_class(monitor_class)(self.indicator_name, monitor_name, monitor_settings)
            ScheduleSetter(monitor.poll, schedule_location)
            return monitor
        except NameError as e:
            message = "{indicator}: implementation for monitor type '{monitor}' " \
                      "is not available or incomplete\n" \
                      "Exception: {exception}\n"
            message = message.format(indicator=self.indicator_name, monitor=monitor_name, exception=e)
            logger.error(message)

    def find_schedule(self, monitor_settings):
        if 'schedule' in monitor_settings:
            return monitor_settings
        elif 'schedule' in self.settings:
            return self.settings
        else:
            return o_conf().defaults

    def run(self):
        logger.info('Indicator {indicator}: running...'.format(indicator=self.indicator_name))
        for monitor in self.monitors:
            logger.info("{indicator}: polling '{name}' tests"
                           .format(indicator=self.indicator_name, name=monitor.name))
            monitor.poll()

    def poll_bamboo(self):
        logger.info('Signal {signal}: polling...'.format(signal=self.indicator_name))
        try:
            bamboo_results = self.bamboo_tasks.all_results() if self.bamboo_tasks else None
            sitemap_ok = self.sitemap.urls_ok() if self.sitemap else True
        except Exception as e:
            logger.error('Signal {signal}: Unhandled internal exception. '
                         'Could be configuration problem or bug.\n{exception}'
                         .format(signal=self.indicator_name, exception=e.args))
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
        logger.error("Signal {signal}: internal exception occurred:\n{exception}".format(signal=self.indicator_name,
                                                                                         exception=e))
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
            sound = self.monitors['sounds']
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
        message = "State changing from '{previous}' to '{current}'" \
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
        Persist.store(self.state_id(), state)

# TODO: BSM/New Relic
# TODO: Geckoboard
