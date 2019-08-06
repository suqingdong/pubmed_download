# -*- coding: utf-8 -*-
import sys
from urllib import urlencode

import scrapy

from pubmed_download.utils.user_agent import UserAgent as UA
from pubmed_download.utils.parse_xml import parse_pubmed_xml


reload(sys)
sys.setdefaultencoding('utf-8')


class PubmedSpiderSpider(scrapy.Spider):
    name = 'pubmed_spider'
    allowed_domains = ['ncbi.nlm.nih.gov']

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def start_requests(self):

        base_url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?'

        retmax = int(self.kwargs.get('retmax', 250))
        start = int(self.kwargs.get('start', 1))

        limit = int(self.kwargs.get('limit', 0))

        while True:

            if self.kwargs.get('pmid'):
                id_list = self.kwargs['pmid']
                self.logger.info(
                    '\033[32mcrawling pmid: {}\033[0m'.format(self.kwargs['pmid']))
            else:
                self.logger.info(
                    '\033[32mcrawling pmid {} - {}\033[0m'.format(start, start + retmax - 1))
                id_list = ','.join(str(i) for i in range(start, start + retmax))

            params = {
                'db': 'pubmed',
                'retmode': 'xml',
                'id': id_list
            }
            if self.kwargs.get('api_key'):
                params['api_key'] = self.kwargs['api_key']

            url = base_url + urlencode(params)

            yield scrapy.Request(url, headers=UA.random_ua())

            start += retmax
            if self.kwargs.get('pmid') or (limit and start > limit):
                break

    def parse(self, response):

        # 没有数据时会自动停止爬虫
        for context in parse_pubmed_xml(response.text):
            if context is None:
                self.crawler.engine.close_spider(self, 'no article any more')
            else:
                yield context

