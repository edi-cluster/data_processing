#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 23:42:08 2022

@author: rashev
"""

import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.r']
    #start_urls = ['https://izhevsk.hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&text=python&items_on_page=20&no_magic=true&L_save_area=true',
    #              'https://izhevsk.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=python&items_on_page=20&no_magic=true&L_save_area=true']
    #start_urls = ['https://spb.hh.ru/search/vacancy?text=python&from=suggest_post&fromSearchLine=true&area=2']
    stats_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python&geo%5Bt%5D%5B0%5D=4']
    
    def parse(self, response: HtmlResponse):
        print()
        next_page = response.xpath("//a[@rel='next']/@href").get()
#        if next_page:
#            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@contains('_1IHWd')]/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)


    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1/text()").get()
        salary = response.xpath("//span[@class='_2eYAG _10_Fa _21QHd _9Is4f']/text()").getall()
        url = response.url
        yield JobparserItem(name=name, salary=salary, url=url)
