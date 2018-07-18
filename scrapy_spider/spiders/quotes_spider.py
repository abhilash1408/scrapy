# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.selector import Selector
class QuotesSpiderSpider(scrapy.Spider):
    name = 'quotes_spider'
    allowed_domains = ['www.booking.com']
    start_urls = ['https://www.booking.com/searchresults.en-gb.html?city=-2106102']
    items=[]


    def parse(self, response):
        with open('config.json') as json_file:
            config = json.load(json_file)
            sel = Selector(response)
            hotelsLinks = sel.xpath(config["htmltags"]["linkpath"]).extract()
            i = hotelsLinks[0]
            link = i[1:-1]
            link = link.split('?',1)
            yield scrapy.Request(config["htmltags"]["base_url"]+link[0]+config["htmltags"]["checkin"]+config["htmltags"]["checkout"],callback=self.parse_hotel)
            # for i in hotelsLinks:
            #     link = i[1:-1]
            #     link = link.split('?',1)
            #     yield scrapy.Request(config["htmltags"]["base_url"]+link[0]+config["htmltags"]["checkin"]+config["htmltags"]["checkout"],callback=self.parse_hotel)

            # hotel={}
            # hotel['name']=hotelsList.css(config["htmltags"]["namecss"]).extract_first()[1:-1]
            # hotel['link'] = hotelsList.xpath(config["htmltags"]["linkpath"]).extract_first()[1:-1]
            # hotel['rating'] = hotelsList.xpath(config["htmltags"]["ratingpath"]).extract_first()[1:-1]
            # print(hotel)
            #print(hotelsList[0].xpath(config["htmltags"]["roomtype"]))
            #hotel['price'] =i.xpath(config["htmltags"]["pricepath"]).extract()

    def parse_hotel(self,response):
        with open('config.json') as json_file:
            config = json.load(json_file)
            hotel={}
            sel = Selector(response)
            hotel['title']=sel.xpath(config["htmltags"]["title"])[0].extract()[1:-1]

            starsElement = sel.css(config["htmltags"]["starsElement"])
            hotel['stars'] = starsElement.css(config["htmltags"]["stars"])[0].extract()
            address = sel.css("#showMap2")
            ad = address.xpath("span/text()")[0].extract()
            hotel['address'] = ad[1:-1]
            print(hotel)
        
        
                

                

        



