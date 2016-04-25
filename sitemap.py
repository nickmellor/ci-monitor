from proxies import proxies
import requests
from xml.etree import ElementTree
from logger import logger


class Sitemap:

    def __init__(self, settings):
        self.sitemaps = settings

    def poll(self):
        faults = []
        for sitemap_name, sitemap in self.sitemaps:
            for url in self.extracted_urls(sitemap):
                url_response = requests.get(url, verify=False, proxies=proxies)
                if not 200 <= url_response.status_code < 300:
                    faults += (sitemap_name, url, url_response.status_code)

    def extracted_urls(self, uri):
        sitemap = self.sitemap_xml(uri)
        if sitemap:
            tree = ElementTree.parse(sitemap)
            root = tree.getroot()
            for node in root.iter('node'):
                for url in node.iter("loc"):
                    yield url.text

    @staticmethod
    def sitemap_xml(uri):
        try:
            response = requests.get(uri, verify=False, proxies=proxies)
            return response.text
        except ConnectionError as e:
            logger.error("Sitemap: sitemap unavailable:\n{0}".format(e))
            return None
