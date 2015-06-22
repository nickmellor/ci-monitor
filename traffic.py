import random
import os
import sound


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self, monitored_environments):
        self.old_colour = None
        self.monitored_environments = monitored_environments
        self.finished_without_unhandled_exceptions = True

    def signal_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = False

    def clear_unhandled_exception(self):
        self.finished_without_unhandled_exceptions = True

    def change_lights(self, new_colour):
        # ignore requests to change lights if last run had an unhandled exception
        # lights quietly stay all on rather than doing the Christmas Tree lights thing
        # every few seconds
        # TODO: unhandled_exceptions check belongs in ci_monitor.py and bamboo.py
        if self.finished_without_unhandled_exceptions:
            self.blank()  # Blink health check
            if new_colour != self.old_colour:
                # draw some attention to change
                self.christmas_lights()
                print('Light changing from {0} to {1}!'.format(self.old_colour, new_colour))
                self.old_colour = new_colour
                sound.play_sound(self.old_colour, new_colour)
            self.set_lights(new_colour)

    def blank(self):
        self.set_lights('off')

    def christmas_lights(self):
        for i in range(20):
            self.set_lights(random.choice(['red', 'yellow', 'green']))

    def set_lights(self, colour_or_colours):
        traffic_light_lamp_configs = {
            'green': (0, 0, 1),
            'yellow': (0, 1, 0),
            'red': (1, 0, 0),
            'off': (0, 0, 0),
            'all': (1, 1, 1),
            'redyellow': (1, 1, 0)
        }
        lamp_settings = dict(zip(['red', 'yellow', 'green'], traffic_light_lamp_configs[colour_or_colours]))
        # TODO: make able to run separate traffic light devices from same box
        os.system("./clewarecontrol -d 901880 -c 1 -as 0 {red} -as 1 {yellow} -as 2 {green}".format(**lamp_settings))

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
        colours = 'redyellow' if comms_failure and not all_passed else colours
        self.change_lights(colours)
