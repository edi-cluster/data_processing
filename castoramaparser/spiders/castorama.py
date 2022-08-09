import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from castoramaparser.items import CastoramaparserItem


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['castorama.ru']
    start_urls = ['https://www.castorama.ru/catalogsearch/result/?q=%D1%88%D0%BA%D0%B0%D1%84']  # шкаф

    def parse(self, response: HtmlResponse):
        nnext = response.xpath("//div[@class='pager']//li//a[@class='next i-next']/@href").get()

        if nnext:
            yield response.follow(nnext, callback=self.parse)

        for link in response.xpath("//ul[contains(@class, 'products-grid')]//a[@class='product-card__img-link']"):
            yield response.follow(link, callback=self.page_parser)

    def page_parser(self, response: HtmlResponse):
        loader = ItemLoader(item=CastoramaparserItem(), response=response)
        loader.add_xpath('price',
                         "//div[contains(@class, 'add-to-cart__price')]//div[@class='current-price']//span//text()")
        loader.add_xpath('photo', "//li[contains(@class, 'top-slide')]//@data-src")
        loader.add_xpath('name', "//h1/text()")
        # loader.add_xpath('_id', "//span[@itemprop='sku']/text()")
        loader.add_value('link', response.url)
        yield loader.load_item()
