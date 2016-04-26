from proxies import proxies
import requests
import xml.etree.ElementTree as ET
from logger import logger
import yaml


class Sitemap:

    def __init__(self, settings):
        self.sitemaps = settings

    def poll(self):
        faults = []
        for sitemap_name, sitemap in self.sitemaps.items():
            for url in self.extracted_urls(sitemap):
                url_response = requests.get(url, verify=False, proxies=proxies)
                if not 200 <= url_response.status_code < 300:
                    faults += (sitemap_name, url, url_response.status_code)
        if faults:
            message = ['*' * 40]
            message.extend(faults)
            message.append('*' * 40)
            logger.error(faults)

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


if __name__ == '__main__':
    with open('conf.yaml') as config_file:
        settings = yaml.load(config_file)['signallers']['SITEMAP_TEST']['sitemap']
    s = Sitemap(settings)
    s.poll()
    # repo = Repo('scratch/repos/integration-services')
    # d = repo.heads['develop'].commit.committed_date
    # print(time.gmtime(d))
