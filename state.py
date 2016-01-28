class State:
    """saves state of a device or signal across configuration changes"""

    state = {}

    @classmethod
    def store(cls, item, state):
        cls.state.update({item: state})

    @classmethod
    def retrieve(cls, item, default=None):
        return cls.state.get(item, default)

