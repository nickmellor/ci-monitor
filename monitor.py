class Monitor:

    def __init__(self, indicator, monitor_class, settings):
        self.monitor_class = monitor_class
        self.indicator = indicator
        self.settings = settings
        self.name = self.settings.name

        self.old_state = None
        self.state = None
        self.set_state('allTestsPassed')
        self.changed = False

    # def state_change(self):
    #     raise NotImplementedException("'state_change()' method not implemented")

    def tests_ok(self):
        raise NotImplementedException("'ok()' method not implemented")

    def comms_ok(self):
        raise NotImplementedException("'comms_ok()' method not implemented")

    def has_changed(self):
        raise NotImplementedException("'has_changed()' method not implemented")

    def poll(self):
        raise NotImplementedException("'poll()' method not implemented")

    def set_state(self, value):
        self.state = value


class NotImplementedException(Exception):
    pass
