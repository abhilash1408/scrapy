# -*- coding: utf-8 -*-
import scrapy
import json
from scrapy.selector import Selector
class QuotesSpiderSpider(scrapy.Spider):
    name = 'quotes_spider'
    allowed_domains = ['www.booking.com']
    start_urls = ['https://www.booking.com/searchresults.en-gb.html?city=-2106102']
    data = {}


    def parse(self, response):
        with open('config.json') as json_file:
            config = json.load(json_file)
            hotelsList = response.xpath(config["htmltags"]["hotelslistelement"])

            #hotelElements = hotelsList.xpath(config["htmltags"]["hotelelementclass"])
            for i in hotelsList:
                
                #names=i.xpath(config["htmltags"]["namepath"])
                names=i.css(config["htmltags"]["namecss"])
                for k in names:
                    print(k.extract())
                #hotel['link'] = i.xpath(config["htmltags"]["linkpath"]).extract()
                #hotel['rating'] = i.xpath(config["htmltags"]["ratingpath"]).extract()
                #hotel['type'] = i.xpath(config["htmltags"]["roomtype"]).extract()
                #hotel['price'] =i.xpath(config["htmltags"]["pricepath"]).extract()
                

        



