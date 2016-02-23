import os
import subprocess
from logger import logger
from conf import conf
from time import sleep
from state import State

settings = conf['states']


class TrafficLight:
    """
    use one class instance per traffic light device
    """

    def __init__(self, signaller, tlight_settings):
        self.signaller = signaller  # just for logging
        self.device_id = tlight_settings['id']
        logger.info("Traffic light device '{device}' is being used by signal '{signaller}'"
                    .format(device=self.device_id, signaller=signaller))

    def previous_state(self):
        return State.retrieve(self.previous_state_cache_key())

    def store_state(self, state):
        State.store(self.previous_state_cache_key(), state)

    def previous_state_cache_key(self):
        return 'tlight:{device_id}:previousState'.format(device_id=self.device_id)

    def previously_connected(self):
        return State.retrieve(self.connected_cache_key(), True)

    def connected_cache_key(self):
        return 'tlight:{device_id}:connected'.format(device_id=self.device_id)

    def blink(self):
        self.all_lamps_off()
        sleep(settings['blinktime_secs'])
        self._set_lamps(self.previous_state(), monitor=False)

    def all_lamps_off(self):
        self._set_lamps('blank', monitor=False)

    def lights_changing(self, new_state):
        for i in range(3):
            self._set_lamps('changestate', monitor=False)
            self._set_lamps('blank', monitor=False)
        if self.previously_connected():
            logger.info("{signaller}: device '{device}': light changing from '{old}' to '{new}'"
                        .format(signaller=self.signaller, device=self.device_id,
                                old=self.previous_state(), new=new_state))
        self._set_lamps(new_state)
        self.set_state(new_state)

    def set_state(self, new_state):
        State.store(self.previous_state_cache_key(), new_state)

    def set_lights(self, new_state):
        if new_state != self.previous_state():
            self.lights_changing(new_state)
        else:
            self.blink()

    def _set_lamps(self, state, monitor=True):
        shell_command = self._shell_command(state)
        if monitor and self.previously_connected():
            logger.info("Executing shell command for traffic light: '{0}'".format(shell_command))
        stdout, error = subprocess.Popen(shell_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         shell=True).communicate()
        device_detected = not (stdout or error)  # device drivers missing/device missing not differentiated
        if not device_detected:
            if self.previously_connected():
                message = "Signaller '{signaller}' traffic light '{device}' is not responding.\n" \
                          "No further warnings for this traffic light will be given until it is connected.\n"
                message += "Message: '{message}'\n"
                message = message.format(signaller=self.signaller, device=self.device_id,
                                         message=stdout.decode('UTF-8').strip())
                logger.info(message)
        self.store_connection_status(device_detected)

    def store_connection_status(self, device_detected):
        State.store(self.connected_cache_key(), device_detected)

    def _shell_command(self, state):
        lamp_pattern = settings['lamppatterns'][state]
        colour_to_switch = {'red': 'R', 'yellow': 'Y', 'green': 'G', 'alloff': 'O'}
        # spaces between lamp switches on command line
        lamp_switches = ' '.join(colour_to_switch[lamp] for lamp in lamp_pattern)
        if not lamp_switches:
            lamp_switches = 'O'
        lamps = "{lamps}".format(lamps=lamp_switches)
        verb = os.path.join(".", "usbswitchcmd")
        device = "-n {device}".format(device=str(self.device_id))
        shell_command = "{verb} {device} {lamps}".format(verb=verb, device=device, lamps=lamps)
        return shell_command
