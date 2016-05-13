import datetime

# needs to be config reload-proof
from state import State


class Wait:
    """
    tool for periodic long-running monitor processes that shouldn't run at every heartbeat
    """
    def __init__(self, state_id):
        # always run on startup
        self._nextrun = datetime.datetime.now()
        self.state_base_id = state_id
        self._set_override()
        self._set_interval_timestamp()
        self.seconds = None
        self.schedule = None

    def reset_poll_queue(self):
        self._set_poll_queue([])

    def set_interval(self, seconds):
        self.seconds = seconds

    def set_schedule(self, times):
        self.schedule = {time: self.today_at(time) >= now() for time in times}

    def _set_override(self, tf=None):
        if tf is not None:
            State.store(self._override_state_id(), tf)
        elif not self._override_state_id() in State.state:
            # default for first time
            self._set_override(True)

    def _set_interval_timestamp(self, dt=None):
        if dt is not None:
            State.store(self._timestamp_state_id(), dt)
        elif not self._timestamp_state_id() in State.state:
            self._set_interval_timestamp(now())

    def poll_now(self):
        if self._override():
            self._set_override(False)
            return True
        else:
            timeout = (now() - self._timestamp()).seconds > self.seconds
            if timeout:
                self._set_interval_timestamp(now())
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

    def today_at(self, string_date):
        time_portion = datetime.datetime.strptime('11:20AM', '%I:%M%p')
        t = datetime.datetime.today()
        return time_portion.replace(year=t.year, month=t.month, day=t.day)

    def build_poll_queue(self):
        times = []
        if self.schedule:
            times += [self.today_at(time) for time, polled in self.schedule.items() if not polled]
        if self.seconds:
            next_interval_time = self._timestamp()
            if next_interval_time <= now():
               times += [next_interval_time]
               self._set_interval_timestamp(next_interval_time + datetime.timedelta(seconds=self.seconds))

def now():
    return datetime.datetime.now()

if __name__ == '__main__':
    pass