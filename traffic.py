import os
import subprocess
from logger import logger
from conf import conf
from time import sleep

global_settings = conf['trafficlights'] # settings for all traffic lights


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self, signaller, device):
        self.signaller = signaller # just for logging
        self.device = device
        logger.info("Device '{device}' is monitoring environments for '{signaller}'".format(
            device=device, signaller=', '.join(signaller)))
        self.device_was_connected_last_time = True

    def blink(self):
        self.blank()
        sleep(global_settings['blinktime_secs'])

    def blank(self):
        self.set_lights('blank')

    def change_lights(self, new_state, old_state, errorlevel):
        for i in range(3):
            self.set_lights('changestate')
            self.set_lights('blank')
        message = "Light changing from '{0}' to '{1}'".format(old_state, new_state)
        {'ERROR': logger.error,
         'WARNING': logger.warn,
         'NONE': logger.info}[errorlevel](message)
        self.set_lights(new_state)

    def set_lights(self, pattern_name):
        lamp_pattern = global_settings['lamppatterns'][pattern_name]
        colour_to_switch = {'red': 'R', 'yellow': 'Y', 'green': 'G', 'alloff': 'O'}
        # spaces between lamp switches on command line
        lamp_switches = ' '.join(colour_to_switch[lamp] for lamp in lamp_pattern)
        if not lamp_switches:
            lamp_switches = 'O'
        cmd_switches = "{switches}".format(switches=lamp_switches)
        cmd_verb = os.path.join(".", "usbswitchcmd")
        cmd_device = "-n {device}".format(device=str(self.device))
        shellCmd = "{verb} {device} {switches}".format(verb=cmd_verb, device=cmd_device, switches=cmd_switches)
        logger.info("Executing shell command for traffic light: '{0}'".format(shellCmd))
        stdout, error = subprocess.Popen(shellCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
        device_is_missing = True if stdout else False
        if device_is_missing:
            if self.device_was_connected_last_time:
                message = "Signaller '{signaller}' traffic light '{device}' is not responding.\n" \
                          "No further warnings for this traffic light will be given\n"
                message += "Message: '{message}'\n"
                message = message.format(signaller=self.signaller, device=self.device,
                                         message=stdout.decode('UTF-8').strip())
                logger.warning(message)
                self.device_was_connected_last_time = False
        else:
            self.device_was_connected_last_time = True
