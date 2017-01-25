import xml.etree.ElementTree as ET

from requests import get
from requests.exceptions import RequestException
from requests.packages.urllib3.exceptions import MaxRetryError

from listener import Listener
from listeners.support.url_checker import UrlChecker
from utils.logger import logger
from utils.message import Message


class Sitemap(Listener):

    def __init__(self, indicator_name, listener_class, settings):
        super().__init__(indicator_name, listener_class, settings)
        self.sitemap = settings['file']
        self.all_good = True

    def poll(self):
        errors = []
        extracted_urls = list(self.extracted_urls(self.sitemap))
        url_count = len(extracted_urls)
        if extracted_urls:
            errors = UrlChecker(extracted_urls, error_texts()).run()
        else:
            logger.error("Sitemap '{name}' ({sitemap}) not available".format(name=self.name, sitemap=self.sitemap))
            errors.append((self.name, self.sitemap, 'sitemap file not available'))
        if errors:
            message = ["Sitemap errors for '{name}' ({sitemap}) as follows:".format(name=self.name, sitemap=self.sitemap),
                       '*' * 125]
            message.extend('* {no}. {fault}'.format(no=n + 1, fault=reportable_fault)
                           for n, reportable_fault
                           in enumerate(repr(error) for error in errors))
            message.append('*** {0} failures testing {1} urls'.format(len(errors), url_count))
            message.append('*' * 125)
            logger.error('\n'.join(message))
        else:
            logger.info("All {count} sitemap URLs ok for '{name}' ({sitemap})".format(count=url_count, name=self.name, sitemap=self.sitemap))
        self.all_good = not errors

    def extracted_urls(self, uri):
        sitemap_as_string = self.sitemap_xml(uri)
        if sitemap_as_string:
            try:
                sitemap = ET.fromstring(sitemap_as_string)
            except ET.ParseError as e:
                message = Message("""
{indicator}: Error parsing sitemap '{sitemap}'
{lines} lines in sitemap XML file
Sitemap reads as follows:""")
                message.indent()
                message.add_text_summary(sitemap_as_string)
                message.outdent()
                message.add('Exception raised:')
                message.add_text('{exception}')
                logger.error(message.out().format(
                    indicator=self.indicator_name,
                    sitemap=uri,
                    lines=len(sitemap_as_string.splitlines()),
                    exception=e)
                )
                logger.info('Sitemap length: {0}'.format(len(sitemap_as_string)))
            else:
                for url in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    yield url.text

    def tests_ok(self):
        return self.all_good

    def comms_ok(self):
        # TODO: comms error if can't reach URLs
        return True

    @staticmethod
    def sitemap_xml(uri):
        try:
            response = get(uri)
            return response.text
        except (RequestException, ConnectionError, MaxRetryError) as e:
            logger.error("Sitemap: sitemap unavailable:\n{0}".format(e))
            return None

    def has_changed(self):
        return False


def error_texts():
    return [
        # 'could not process request',
        # 've encountered a problem.',
        # 'Sorry, but it looks like the page you are looking for could not be found.'
        '5222',
        '132 331'
    ]
