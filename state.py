class State:
    """saves state of a device or signal across configuration changes"""

    state = {}

    @classmethod
    def store(self, item, state):
        self.state.update({item: state})

    @classmethod
    def retrieve(self, item):
        return self.state.get(item)

