import random
import os
import sound
from logger import logger
from conf import conf
from time import sleep


traffic_light_lamp_configs = {
    'green': (0, 0, 1),
    'yellow': (0, 1, 0),
    'red': (1, 0, 0),
    'off': (0, 0, 0),
    'all': (1, 1, 1),
    'redyellow': (1, 1, 0),
    'commserror': (1, 1, 0),
    'changestate': (1, 0, 1),
}


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self):
        self.old_colour = None
        self.monitored_environments = conf['trafficlight']['environments']
        self.finished_without_unhandled_exceptions = True

    def signal_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = False

    def clear_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = True

    def blink(self):
        self.blank()
        sleep(conf['trafficlight']['blinktimesecs'])

    def change_lights(self, new_colour):
        # ignore requests to change lights if last run had an unhandled exception
        # lights quietly stay all on rather than doing the Christmas Tree lights thing
        # every few seconds
        # TODO: unhandled_exceptions check belongs in ci_monitor.py and bamboo.py
        if self.finished_without_unhandled_exceptions:
            self.blink() # check traffic app hasn't crashed
            if new_colour != self.old_colour:
                # draw some attention to change
                self.draw_attention_to_state_change()
                logger.info('Light changing from {0} to {1}!'.format(self.old_colour, new_colour))
                self.old_colour = new_colour
                sound.play_sound(self.old_colour, new_colour)
            self.set_lights(new_colour)

    def blank(self):
        self.set_lights('off')

    def draw_attention_to_state_change(self):
        for i in range(3):
            self.set_lights('changestate')
            self.set_lights('off')

    def set_lights_RPi(self, colour_or_colours_name):
        lamp_settings = dict(zip(['red', 'yellow', 'green'], traffic_light_lamp_configs[colour_or_colours_name]))
        os.system("./clewarecontrol -d 901880 -c 1 -as 0 {red} -as 1 {yellow} -as 2 {green}".format(**lamp_settings))

    def set_lights(self, pattern_name):
        pattern = traffic_light_lamp_configs[pattern_name]
        lamps = 'R' if pattern[0] else ''
        lamps += 'Y' if pattern[1] else ''
        lamps += 'G' if pattern[2] else ''
        if lamps:
            lamps = ' '.join(lamps)
        else:
            lamps = 'O'
        os.system(".\\usbswitchcmd -n 901880 {lamps}".format(lamps=lamps))

    def big_trouble(self):
        self.change_lights('all')

    def show_results(self, results):
        all_passed = True
        comms_failure = False
        for env in self.monitored_environments:
            env_results = results[env].values()
            all_passed = all_passed and all(passed for passed in env_results)
            # can be yellow if there is a comms failure and no failed tests up til now
            if any(passed is None for passed in env_results):
                comms_failure = True
        colours = 'green' if all_passed else "yellow" if comms_failure else "red"
        colours = 'commserror' if comms_failure and not all_passed else colours
        self.change_lights(colours)
