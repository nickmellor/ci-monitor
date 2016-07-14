import os
import subprocess
from time import sleep

from conf import configuration, o_conf
from utils.logger import logger

settings = configuration['states']


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self, indicator, device_settings):
        self.indicator = indicator  # just for logging
        self.device_id = device_settings['id']
        logger.info("Traffic light device '{device}' is being used by indicator '{indicator}'"
                    .format(device=self.device_id, indicator=indicator))
        self.state = None
        self.connected = True

    def blink(self):
        self.all_lamps_off()
        sleep(o_conf().lights.blinktime_secs)
        self.set_lights(self.state, monitor=False)

    def state_change(self):
        for times in range(3):
            self.set_lights('statechange', monitor=False)
            self.set_lights('blank')

    def all_lamps_off(self):
        self.set_lights('blank', monitor=False)

    def set_lights(self, state, monitor=True):
        shell_command = self._shell_command(state)
        if monitor and self.connected:
            logger.info("Executing shell command for traffic light: '{0}'".format(shell_command))
        stdout, error = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         shell=True).communicate()
        # device drivers missing/device missing not differentiated
        device_detected = not (stdout or error)
        if self.connected:
            if not device_detected:
                message = "Indicator '{indicator}' traffic light '{device}' is not responding.\n" \
                          "No further warnings for this traffic light will be given until it is connected.\n"
                message += "Error message: '{message}'\n"
                message = message.format(indicator=self.indicator, device=self.device_id,
                                         message=stdout.decode('UTF-8').strip())
                logger.warning(message)
        self.connected = device_detected

    def _shell_command(self, state):
        lamp_pattern = o_conf().lights.lamppatterns[state]
        colour_to_switch = {'red': 'R', 'yellow': 'Y', 'green': 'G', 'alloff': 'O'}
        # spaces between lamp switches on command line
        lamp_switches = ' '.join(colour_to_switch[lamp] for lamp in lamp_pattern)
        if not lamp_switches:
            lamp_switches = 'O'
        lamps = "{lamps}".format(lamps=lamp_switches)
        verb = os.path.join(".", "usbswitchcmd")
        device = "-n {device}".format(device=str(self.device_id))
        command = "{verb} {device} {lamps}".format(verb=verb, device=device, lamps=lamps)
        return command
