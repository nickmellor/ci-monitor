from conf import conf
try:
    proxies = {
        "http": conf['proxies']['http'],
        "https": conf['proxies']['https']
    }
except Exception as e:
    proxies = None

