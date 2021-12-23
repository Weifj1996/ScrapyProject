# -*-coding:utf-8-*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import ExampleItem


class ExamplesSpider(scrapy.Spider):
    name = 'examples'
    allowed_domains = ['matplotlib.org']
    start_urls = ['https://matplotlib.org/2.0.2/examples/index.html',]

    def parse(self, response):
        # le = LinkExtractor(restrict_css="div.toctree-wrapper.compound", deny='/index.html$')
        # for link in le.extract_links(response):
        #     yield scrapy.Request(link.url, callback=self.parse_example)

        # response.follow_all
        #links = response.css('div.toctree-wrapper.compound li.toctree-l2 a.reference.internal::attr(href)').getall()
        yield from response.follow_all(css='div.toctree-wrapper.compound li.toctree-l2 a.reference.internal', callback=self.parse_example)

    def parse_example(self, response):
        href = response.css('a.reference.external::attr(href)').get()
        url = response.urljoin(href)
        example = ExampleItem()
        example['file_urls'] = [url]
        return example
