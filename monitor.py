class Monitor:

    def __init__(self, subclass):
        self.subclass = subclass
        self.old_state = None
        self.state = None
        self.set_state('allTestsPassed')
        self.old_comms_ok = True
        self.comms_ok = True
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
