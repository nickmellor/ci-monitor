class NotImplementedException(Exception):
    pass


class Monitor:

    def __init__(self, subclass):
        self.subclass = subclass
        self.old_state = None
        self.state = None
        self.old_comms_ok = True
        self.comms_ok = True
        self.changed = False

    # def state_change(self):
    #     raise NotImplementedException("'state_change()' method not implemented")

    # def ok(self):
    #     raise NotImplementedException("'ok()' method not implemented")
    #
    def comms_error(self):
        return not self.comms_ok

    def poll(self):
        raise NotImplementedException("'poll()' method not implemented")