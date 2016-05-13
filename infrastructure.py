class NotImplementedException(Exception):
    pass


class Infrastructure:

    def __init__(self, subclass):
        self.old_state = None
        self.state = None

    def state_change(self):
        raise NotImplementedException("'state_change()' method not implemented")

    def comms_error(self):
        raise NotImplementedException("'comms_error()' method not implemented")

    def poll(self):
        raise NotImplementedException("'poll()' method not implemented")


