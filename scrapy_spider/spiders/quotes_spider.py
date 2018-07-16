# -*- coding: utf-8 -*-
import scrapy


class QuotesSpiderSpider(scrapy.Spider):
    name = 'quotes_spider'
    ratings=[]
    i=0
    allowed_domains = ['www.booking.com']
    start_urls = ['https://www.booking.com/searchresults.en-gb.html?city=-2106102']


    def parse(self, response):
        links = response.xpath("//a[@class='hotel_name_link url']/@href").extract()
        results = links[:5]
        base_url = 'https://www.booking.com/'
        for link in results:
            full_url = base_url+ link[2:]
            yield scrapy.Request(full_url,callback = self.parse_hotel)
        

    def parse_hotel(self,response):
        name=response.xpath("//h2[@id='hp_hotel_name']/text()").extract()
        rating = response.xpath("//div[@id='js--hp-gallery-scorecard']/@data-review-score").extract()
        self.ratings.append((name,rating))
        self.i+=1
        self.print_ratings()

    def print_ratings(self):
    	if(self.i==5):
        	print("\n hotels and ratings")
        	for rating in self.ratings:
        		print(" {} : {} ".format(rating[0],rating[1]))