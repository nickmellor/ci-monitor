import xml.etree.ElementTree as ET

from requests import get
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from listener import Listener
from listeners.support.url_checker import UrlChecker
from utils.logger import logger
from utils.message import Message


class Urlcheck(Listener):

    def __init__(self, indicator_name, listener_class, settings):
        super().__init__(indicator_name, listener_class, settings)
        self.urls = settings['urls']
        self.name = settings['name']
        self.all_good = True

    def poll(self):
        errors = UrlChecker(self.urls, error_texts()).run()
        if errors:
            message = ["URL errors for '{name}' as follows:".format(name=self.name, sitemap=self.urls),
                       '*' * 125]
            message.extend('* {no}. {fault}'.format(no=n + 1, fault=reportable_fault)
                           for n, reportable_fault
                           in enumerate(repr(error) for error in errors))
            message.append('*** {0} URLs were unavailable'.format(len(errors)))
            message.append('*' * 125)
            logger.error('\n'.join(message))
        else:
            logger.info("All {count} URLs ok for '{name}'".format(count=self.urls, name=self.name))
        self.all_good = not errors

    def tests_ok(self):
        return self.all_good

    def comms_ok(self):
        # TODO: comms error if can't reach URLs
        return True

    def has_changed(self):
        return False


def error_texts():
    return [
        'website is currently disabled',
    ]
