import os
import subprocess
from logger import logger
from conf import conf
from time import sleep

settings = conf['trafficlights']


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self, signaller, device):
        self.signaller = signaller  # just for logging
        self.device = device
        logger.info("Device '{device}' is being used by signal '{signaller}'"
            .format(device=device, signaller=signaller))
        self.device_was_connected_last_time = True
        self.state = None

    def blink(self):
        self.blank()
        sleep(settings['blinktime_secs'])
        self._set_lamps(self.state)

    def blank(self):
        self._set_lamps('blank')

    def change_lights(self, new_state, old_state, errorlevel):
        self.show_lamp_change()
        message = "Light changing from '{0}' to '{1}'".format(old_state, new_state)
        logger_method = {'ERROR': logger.error,
                     'WARNING': logger.warn,
                     'NONE': logger.info}
        logger_method[errorlevel](message)
        self._set_lamps(new_state)

    def show_lamp_change(self):
        for i in range(3):
            self._set_lamps('changestate', monitor=False)
            self._set_lamps('blank', monitor=False)

    def set_lights(self, new_state):
        if new_state != self.state:
            self.show_lamp_change()
            self._set_lamps(new_state)
            self.state = new_state
        else:
            # off and on quickly to show process is still alive
            self.blink()

    def _set_lamps(self, state, monitor=True):
        shell_command = self._shell_command(state)
        if monitor:
            logger.info("Executing shell command for traffic light: '{0}'".format(shell_command))
        stdout, error = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         shell=True).communicate()
        device_is_missing = True if stdout or error else False
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

    def _shell_command(self, state):
        lamp_pattern = settings['lamppatterns'][state]
        colour_to_switch = {'red': 'R', 'yellow': 'Y', 'green': 'G', 'alloff': 'O'}
        # spaces between lamp switches on command line
        lamp_switches = ' '.join(colour_to_switch[lamp] for lamp in lamp_pattern)
        if not lamp_switches:
            lamp_switches = 'O'
        cmd_switches = "{switches}".format(switches=lamp_switches)
        cmd_verb = os.path.join(".", "usbswitchcmd")
        cmd_device = "-n {device}".format(device=str(self.device))
        shellCmd = "{verb} {device} {switches}".format(verb=cmd_verb, device=cmd_device, switches=cmd_switches)
        return shellCmd
