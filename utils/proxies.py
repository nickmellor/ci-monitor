from conf import raw_conf

try:
    proxies = {
        "http": raw_conf()['proxies']['http'],
        "https": raw_conf()['proxies']['https']
    }
except KeyError as e:
    proxies = None

