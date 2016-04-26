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

    def urls_all_available(self):
        faults = []
        for sitemap_name, sitemap in self.sitemaps.items():
            for url in self.extracted_urls(sitemap):
                response = requests.get(url, verify=False, proxies=proxies)
                if errorpage(response):
                    faults += (sitemap_name, url, response.status_code)
        if faults:
            message = ['*' * 40]
            message.extend(faults)
            message.append('*' * 40)
            logger.error('\n'.join(message))
        return not faults

    def extracted_urls(self, uri):
        sitemap_as_string = self.sitemap_xml(uri)
        if sitemap_as_string:
            sitemap = ET.fromstring(sitemap_as_string)
            for url in sitemap.iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                yield url.text

    @staticmethod
    def sitemap_xml(uri):
        try:
            response = requests.get(uri, verify=False, proxies=proxies)
            return response.text
        except ConnectionError as e:
            logger.error("Sitemap: sitemap unavailable:\n{0}".format(e))
            return None


def errorpage(response):
    """error pages return 200 so need to check error page text"""
    res = not 200 <= response.status_code < 300
    text = tidy(strip_tags(response.text))
    res = res and not('page not found' in text)
    res = res and not('could not process request' in text)
    return res


def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def tidy(s):
    return re.sub('\s+', ' ', s.lower().strip())


class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ' '.join(self.fed)

if __name__ == '__main__':
    with open('conf.yaml') as config_file:
        settings = yaml.load(config_file)['signallers']['SITEMAP_TEST']['sitemap']
    s = Sitemap(settings)
    s.urls_not_available()