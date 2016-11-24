from listeners.support.markup_stripper import MarkupStripper
import requests
from utils.proxies import proxies
import re
from utils.logger import logger


class UrlChecker:
    def __init__(self, urls, error_texts, source=''):
        self.urls = urls
        self.error_texts = error_texts
        self.source = source

    def run(self):
        errors = []
        for url in self.urls:
            try:
                response = get(url)
            except (RequestException, ConnectionError, MaxRetryError) as e:
                errors.append((self.source, url, repr(e)))
            else:
                pe = page_error(response)
                if pe:
                    errors.append((self.source, url, pe))
                    logger.info("{source} -> '{url}' ...OOPS!".format(source=self.source, url=url))
                else:
                    logger.info("{source} -> '{url}' ok".format(source=self.source, url=url))
            if response.history:
                logger.info("Request was redirected")
                for resp_history_item in response.history:
                    logger.info('{0}: {1}'.format(resp_history_item.status_code, resp_history_item.url))
                logger.info("Final destination:")
                logger.info('{0}: {1}'.format(response.status_code, response.url))
        return errors


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
        # 'could not process request',
        # 've encountered a problem.',
        # 'Sorry, but it looks like the page you are looking for could not be found.'
        '5222',
        '132 331'
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
