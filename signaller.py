import soundplayer
from logger import logger
from conf import conf
from traffic import TrafficLight

settings = conf['trafficlights']


class Signaller:
    """
    glues environments to methods of signalling (traffic lights, sounds)
    """

    def __init__(self, signal_name):
        self.old_state = None
        self.name = signal_name
        self.signal_settings = conf['signallers'][signal_name]
        self.environments = self.signal_settings['environments']
        logger.info("'{signaller}' signal is monitoring environments '{environments}'".format(
            signaller=signal_name, environments=', '.join(self.environments)))
        self.unhandled_exception = False
        self.trafficlight = TrafficLight(signal_name, self.signal_settings['trafficlightid'])

    def signal_unhandled_exception(self):
        self.unhandled_exception = True

    def clear_unhandled_exception(self):
        self.unhandled_exception = False

    def change_lights(self, new_state):
        # ignore requests to change lights if last run had an unhandled exception
        # (wait for stable recovery)
        if not self.unhandled_exception:
            self.trafficlight.blink()  # visual check to make sure ci-monitor hasn't crashed
            if new_state != self.old_state:
                self.state_change(new_state, self.old_state)
                self.old_state = new_state
            self.trafficlight.set_lights(new_state)

    def state_change(self, new_state, old_state):
        errors = settings['lamperror']
        new_error = new_state in errors
        warnings = settings['lampwarn']
        new_warning = new_state in warnings
        change_to_from_error = (new_error) != (old_state in errors)
        change_to_from_warning = (new_warning) != (old_state in warnings)
        if change_to_from_error:
            level = 'ERROR'
        elif change_to_from_warning:
            level = 'WARNING'
        else:
            level = 'NONE'
        self.trafficlight.state_change(new_state, old_state, level)
        sound = self.signal_settings['sounds']
        if new_state in errors or new_state in warnings:
            wav = sound['fail']
        else:
            wav = sound['greenbuild']
        soundplayer.playwav(wav)



    def internal_exception(self):
        self.change_lights('internalexception')

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
        self.change_lights(state)
