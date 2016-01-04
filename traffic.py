import random
import os
import sound
from subprocess import Popen
from logger import logger
from conf import conf
from time import sleep


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self):
        self.old_state = None
        self.monitored_environments = conf['trafficlight']['environments']
        self.finished_without_unhandled_exceptions = True

    def signal_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = False

    def clear_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = True

    def blink(self):
        self.blank()
        sleep(conf['trafficlight']['blinktime_secs'])

    def change_lights(self, new_state):
        # ignore requests to change lights if last run had an unhandled exception
        # (wait for stable recovery)
        if self.finished_without_unhandled_exceptions:
            self.blink()  # visual check to make sure ci-monitor hasn't crashed
            if new_state != self.old_state:
                self.draw_attention_to_state_change(new_state, self.old_state)
                self.old_state = new_state
            self.set_lights(new_state)

    def blank(self):
        self.set_lights('blank')

    def draw_attention_to_state_change(self, new_state, old_state):
        for i in range(3):
            self.set_lights('changestate')
            self.set_lights('blank')
        message = "Light changing from '{0}' to '{1}'".format(old_state, new_state)
        # log warnings/errors when moving into *and* out of a warning/error state
        errors = conf['trafficlight']['lamperror']
        warnings = conf['trafficlight']['lampwarn']
        if (new_state in errors) != (old_state in errors):
            logger.error(message)
        elif (new_state in warnings) != (old_state in warnings):
            logger.warning(message)
        else:
            logger.info(message)
        if new_state in errors or new_state in warnings:
            sound.playwav('alarm_beep.wav')
        else:
            sound.playwav('applause.wav')
        # sound.play_sound(self.old_state, new_state)




    def set_lights(self, pattern_name):
        lamp_config = conf['trafficlight']['lamppatterns'][pattern_name]
        lookup = {'red': 'R', 'yellow': 'Y', 'green': 'G', 'alloff': 'O'}
        # spaces between lamp switches on command line
        lamp_switches = ' '.join(lookup[lamp] for lamp in lamp_config)
        if not lamp_switches:
            lamp_switches = 'O'
        switches = "{switches}".format(switches=lamp_switches)
        command = os.path.join(".", "usbswitchcmd")
        device = "-n 901880"
        shellCmd = "{command} {device} {switches}".format(command=command, device=device, switches=switches)
        try:
            #os.system(shellCmd)
            sts = Popen(shellCmd, shell=True).wait()
            # TODO: handle error conditions better than can from os.system()
        except Exception as e:
            logger.error('Could not find traffic light')

    def internal_exception(self):
        self.change_lights('internalexception')

    def show_results(self, results):
        all_passed = True
        comms_failure = False
        for env in self.monitored_environments:
            env_results = results[env].values()
            all_passed = all_passed and all(env_results)
            if any(passed is None for passed in env_results):
                comms_failure = True
        state = 'allpassed' if all_passed else "commserror" if comms_failure else "failures"
        state = 'commserrorandfailures' if comms_failure and not all_passed else state
        self.change_lights(state)
