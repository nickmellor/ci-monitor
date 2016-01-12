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

    def __init__(self, signaller, device_id):
        self.signaller = signaller  # just for logging
        self.device_id = device_id
        logger.info("Device '{device}' is being used by signal '{signaller}'"
                    .format(device=device_id, signaller=signaller))
        self.device_was_connected_last_time = True
        self.state = None

    def blink(self):
        self.all_lamps_off()
        sleep(settings['blinktime_secs'])
        self._set_lamps(self.state)

    def all_lamps_off(self):
        self._set_lamps('blank')

    def change_lights(self, new_state, old_state, errorlevel):
        self.lights_changing()
        self._set_lamps(new_state)

    def lights_changing(self, new_state):
        for i in range(3):
            self._set_lamps('changestate', monitor=False)
            self._set_lamps('blank', monitor=False)
        logger.info("Light changing from '{0}' to '{1}'".format(self.state, new_state))
        self._set_lamps(new_state)
        self.state = new_state

    def set_lights(self, new_state):
        if new_state != self.state:
            self.lights_changing(new_state)
        else:
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
                message = message.format(signaller=self.signaller, device=self.device_id,
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
        cmd_lamps = "{switches}".format(switches=lamp_switches)
        cmd_verb = os.path.join(".", "usbswitchcmd")
        cmd_device = "-n {device}".format(device=str(self.device_id))
        shell_command = "{verb} {device} {lamps}".format(verb=cmd_verb, device=cmd_device, lamps=cmd_lamps)
        return shell_command
