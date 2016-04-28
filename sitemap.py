import http

from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import RequestException

from proxies import proxies
import requests
import xml.etree.ElementTree as ET
from logger import logger
import yaml
from html.parser import HTMLParser
import re


class Sitemap:

    def __init__(self, settings):
        self.sitemaps = settings

    def urls_ok(self):
        errors = []
        url_count = 0
        for sitemap_name, sitemap_uri in self.sitemaps.items():
            extracted_urls = list(self.extracted_urls(sitemap_uri))
            url_count += len(extracted_urls)
            if extracted_urls:
                for url in extracted_urls:
                    # url = 'http://www.medibank.com.au/kjhdsagfbvosjdhf'
                    try:
                        response = get_without_proxy(url)
                    except (RequestException, ConnectionError, MaxRetryError) as e:
                        errors.append((sitemap_name, url, repr(e)))
                    else:
                        if page_error(response):
                            errors.append((sitemap_name, url, str(response.status_code)))
                            logger.info("...'{url}' ...oops!".format(url=url))
                        else:
                            logger.info("...'{url}' passed".format(url=url))
            else:
                logger.error("Sitemap '{name}' ({url}) not available".format(name=sitemap_name, url=sitemap_uri))
                errors.append((sitemap_name, sitemap_uri, 'sitemap file not available'))

        if errors:
            message = ['Sitemap errors as follows:', '*' * 40]
            message.extend('* ' + str(n) + '. ' + reportable_fault for n, reportable_fault in enumerate(repr(fault) for fault in errors))
            message.append('* {0} failures testing {1} urls'.format(len(errors), url_count))
            message.append('*' * 40)
            logger.error('\n'.join(message))
        else:
            logger.info("All {0} sitemap URLs ok".format(url_count))
        return not errors

    def extracted_urls(self, uri):
        sitemap_as_string = self.sitemap_xml(uri)
        if sitemap_as_string:
            sitemap = ET.fromstring(sitemap_as_string)
            # for url in list(sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'))[:3]:
            for url in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                yield url.text

    @staticmethod
    def sitemap_xml(uri):
        try:
            response = get_without_proxy(uri)
            return response.text
        except (RequestException, ConnectionError, MaxRetryError) as e:
            logger.error("Sitemap: sitemap unavailable:\n{0}".format(e))
            return None


def get_without_proxy(address):
    # response = requests.get(uri, verify=False, proxies=proxies)
    session = requests.Session()
    session.trust_env = False
    return session.get(address)


def page_error(response):
    """error pages often return 200 so need to check error page text"""
    res = not(200 <= response.status_code < 300)
    text = easy_match(response.text)
    res = res or ('page not found' in text)
    res = res or ('could not process request' in text)
    res = res or ("encountered a problem." in text)
    return res
    # return True


def easy_match(text_with_markup):
    """remove markup and condense multiple white space to single space"""
    text = strip_markup(text_with_markup).lower().strip()
    return re.sub('\s+', ' ', text)


def strip_markup(html):
    s = MarkupStripper()
    s.feed(html)
    return s.text_without_markup()


class MarkupStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def text_without_markup(self):
        """
        markup replaced by space to handle <br/>. Assume markup is between not within words
        """
        return ' '.join(self.text)

if __name__ == '__main__':
    with open('conf.yaml') as config_file:
        settings = yaml.load(config_file)['signallers']['SITEMAP_TEST']['sitemap']
    s = Sitemap(settings)
    s.urls_ok()