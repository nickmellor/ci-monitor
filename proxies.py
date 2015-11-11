from conf import conf
try:
    proxies = {
        "http": conf['proxies']['http'],
        "https": conf['proxies']['https']
    }
except KeyError as e:
    proxies = None

