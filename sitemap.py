from requests.packages.urllib3.exceptions import MaxRetryError
from requests.exceptions import RequestException

import requests
import xml.etree.ElementTree as ET
from logger import logger
import yaml
from html.parser import HTMLParser
import re
from proxies import proxies
from wait import Wait


class Sitemap:

    def __init__(self, settings, signal):
        self.sitemaps = settings['files']
        self.signal = signal
        self.wait = Wait(signal)
        if 'schedule' in settings:
            self.wait.set_schedule(settings['schedule'])
        elif 'interval' in settings:
            self.wait.set_interval(settings['interval'] * 60)

    def state_id(self):
        return 'sitemap state for signal {0}'.format(self.signal)

    def urls_ok(self):
        pn = self.wait.poll_now()
        if not pn:
            return True
        errors = []
        url_count = 0
        for sitemap_name, sitemap_uri in self.sitemaps.items():
            extracted_urls = list(self.extracted_urls(sitemap_uri))
            url_count += len(extracted_urls)
            if extracted_urls:
                for url in extracted_urls:
                    try:
                        response = get(url)
                    except (RequestException, ConnectionError, MaxRetryError) as e:
                        errors.append((sitemap_name, url, repr(e)))
                    else:
                        pe = page_error(response)
                        if pe:
                            errors.append((sitemap_name, url, pe))
                            logger.info("...'{url}' ...oops!".format(url=url))
                        else:
                            logger.info("...'{url}' passed".format(url=url))
                    if response.history:
                        logger.info("Request was redirected")
                        for resp_history_item in response.history:
                            logger.info('{0}: {1}'.format(resp_history_item.status_code, resp_history_item.url))
                        logger.info("Final destination:")
                        logger.info('{0}: {1}'.format(response.status_code, response.url))
            else:
                logger.error("Sitemap '{name}' ({url}) not available".format(name=sitemap_name, url=sitemap_uri))
                errors.append((sitemap_name, sitemap_uri, 'sitemap file not available'))
        if errors:
            message = ['Sitemap errors as follows:', '*' * 79]
            message.extend('* {no}. {fault}'.format(no=n + 1, fault=reportable_fault)
                           for n, reportable_fault
                           in enumerate(repr(error) for error in errors))
            message.append('*** {0} failures testing {1} urls'.format(len(errors), url_count))
            message.append('*' * 79)
            logger.error('\n'.join(message))
        else:
            logger.info("All {count} sitemap URLs ok".format(count=url_count))
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
            response = get(uri)
            return response.text
        except (RequestException, ConnectionError, MaxRetryError) as e:
            logger.error("Sitemap: sitemap unavailable:\n{0}".format(e))
            return None


def get(address):
    response = requests.get(address, allow_redirects=True, proxies=proxies)
    return response


def page_error(response):
    """error pages often return 200 so need to check error page text too"""
    error = not(200 <= response.status_code < 300)
    if error:
        return 'Http code error: {code}'.format(code=response.status_code)
    error = text_error(response)
    if error:
        return "Error text found on page: '{0}'".format(error)
    return ''


def text_error(response):
    text = easy_match(response.text)
    messages = [
        'could not process request',
        've encountered a problem.',
        'Sorry, but it looks like the page you are looking for could not be found.'
    ]
    for message in messages:
        if message in text:
            return message
    else:
        return None


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
        markup replaced by space mainly to interpret <br/> as word boundary
        """
        return ' '.join(self.text)

if __name__ == '__main__':
    # with open('conf.yaml') as config_file:
    #     settings = yaml.load(config_file)['signals']['RetailDEV']['sitemap']
    # s = Sitemap(settings)
    # s.urls_ok()
    import datetime
    datetime.datetime.now()