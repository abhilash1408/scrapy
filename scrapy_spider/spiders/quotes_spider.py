# -*- coding: utf-8 -*-
import scrapy


class QuotesSpiderSpider(scrapy.Spider):
    name = 'quotes_spider'
    ratings=[]
    allowed_domains = ['www.booking.com']
    start_urls = ['https://www.booking.com/searchresults.en-gb.html?city=-2106102']


    def parse(self, response):
        links = response.xpath("//a[@class='hotel_name_link url']/@href").extract()
        results = links[:5]
        base_url = 'https://www.booking.com/'
        for link in results:
        	full_url = base_url+ link[2:]
        	print(full_url)
        	res = scrapy.Request(full_url,callback = self.parse_hotel)
        print(self.ratings)

    def parse_hotel(self,response):
    	print("here")
    	name=response.xpath("//h2[@id='hp_hotel_name']/text()")
    	rating = response.xpath("//div[@id='js--hp-gallery-scorecard']/@data-review-score")
    	self.ratings.append((name,rating))
