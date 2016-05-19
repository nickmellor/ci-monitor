from utils.conf import configuration
try:
    proxies = {
        "http": configuration['proxies']['http'],
        "https": configuration['proxies']['https']
    }
except KeyError as e:
    proxies = None

