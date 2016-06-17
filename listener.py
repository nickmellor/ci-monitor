class Listener:

    def __init__(self, indicator_name, listener_class, settings):
        self.listener_class = listener_class
        self.indicator_name = indicator_name
        self.settings = settings
        self.name = self.settings.name

        self.old_state = None
        self.set_state('allTestsPassed')
        self.changed = False

    # def state_change(self):
    #     raise NotImplementedException("'state_change()' method not implemented")

    def tests_ok(self):
        raise NotImplementedException("'ok()' method not implemented")

    def comms_ok(self):
        return True

    def has_changed(self):
        raise NotImplementedException("'has_changed()' method not implemented")

    def has_improved(self):
        return False

    def has_got_worse(self):
        return False

    def poll(self):
        raise NotImplementedException("'poll()' method not implemented")

    def results(self):
        pass

    def set_state(self, value):
        self.state = value


class NotImplementedException(Exception):
    pass
