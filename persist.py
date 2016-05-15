

class Persist:
    """saves state of a device or signal across configuration changes"""

    persisted_data = {}

    @classmethod
    def store(cls, item, value):
        cls.persisted_data[item] = value

    @classmethod
    def retrieve(cls, item, default=None):
        value = cls.persisted_data.get(item, default)
        cls.store(item, value)
        return value

