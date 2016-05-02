import datetime

# needs to be config reload-proof
from state import State


class Wait:
    """
    tool for periodic long-running monitor processes that shouldn't run at every heartbeat
    """
    def __init__(self, seconds, state_id):
        # always run on startup
        self.state_base_id = state_id
        self._set_override()
        self._set_timestamp()
        self.seconds = seconds

    def _set_override(self, tf=None):
        if tf is not None:
            State.store(self._override_state_id(), tf)
        elif not self._override_state_id() in State.state:
            # default for first time
            self._set_override(True)

    def _set_timestamp(self, dt=None):
        if dt is not None:
            State.store(self._timestamp_state_id(), dt)
        elif not self._timestamp_state_id() in State.state:
            self._set_timestamp(now())

    def poll_now(self):
        if self._override():
            self._set_override(False)
            return True
        else:
            timeout = (now() - self._timestamp()).seconds > self.seconds
            if timeout:
                self._set_timestamp(now())
                return True
            return False

    def _override(self):
        return State.retrieve(self._override_state_id(), default=True)

    def _timestamp(self):
        return State.retrieve(self._timestamp_state_id(), default=datetime.datetime.now())

    def _override_state_id(self):
        return self.state_base_id + ':sitemap:override'

    def _timestamp_state_id(self):
        return self.state_base_id + ':sitemap:timestamp'


def now():
    return datetime.datetime.now()
