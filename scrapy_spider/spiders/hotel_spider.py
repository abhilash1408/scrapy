# -*- coding: utf-8 -*-
import scrapy
import re
import json
from scrapy.selector import Selector
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals


class HotelSpider(scrapy.Spider):
    name = 'hotel_spider'
    allowed_domains = ['www.booking.com']
    items=[]
    basesearchurl='https://www.booking.com/searchresults.en-gb.html?'
    

    def __init__(self, category=None, *args, **kwargs):
        super(HotelSpider, self).__init__(*args, **kwargs)
        self.start_urls = ['https://www.booking.com/']
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self,spider):
        with open('data.json','w') as out :
            json.dump(self.items,out)
        
    def parse(self, response):
        with open("config.json") as con :
            config = json.load(con)
            if(config["queryparams"]["searchbyhotel"]):
                return scrapy.Request("https://www.booking.com/hotel/in/nikko.en-gb.html?checkin=2018-07-19;checkout=2018-07-22;dest_id=-2106102;dest_type=city;dist=0;group_adults=2;",callback = self.parse_hotel)
            else:
                print(response.url)
                searchurl=self.basesearchurl+"no_rooms="+config["queryparams"]["no_rooms"]+"&group_adults="+config["queryparams"]["group_adults"]+"&group_children="+config["queryparams"]["group_children"]+"&ss="+config["queryparams"]["ss"]+"&checkin_monthday="+config["queryparams"]["checkin_monthday"]+"&checkin_month="+config["queryparams"]["checkin_month"]+"&checkin_year="+config["queryparams"]["checkin_year"]+"&checkout_monthday="+config["queryparams"]["checkout_monthday"]+"&checkout_month="+config["queryparams"]["checkout_month"]+"&checkout_year="+config["queryparams"]["checkout_year"]
                return scrapy.Request(searchurl,callback=self.parse_search)

        #searchresults.en-gb.html?city=-2106102
        #return scrapy.FormRequest.from_response(response,formxpath="//form[@id='frm']",formdata={"ss":"New Delhi","checkin_monthday":"19","checkin_month":"7","checkin_year":"2018","checkout_monthday":"22","checkout_month":"7","checkout_year":"2018" },clickdata = { "type": "submit" },callback=self.parse_search)


    def parse_form(self,response):
        print("search completed")
        print(response.url)
    def parse_search(self,response):
        print("\n\n\nSearch url\n\n\n")
        print(response.url +"\n\n\n")
        with open('search.html','wb') as out:
            out.write(response.body)
        with open('config.json') as json_file:
            config = json.load(json_file)
            sel = Selector(response)
            hotelsLinks = sel.xpath(config["htmltags"]["linkpath"]).extract()
            i = hotelsLinks[0]
            link = i[1:-1]
            #print(sel.css(".sr-hotel__name::text").extract_first())
            #yield scrapy.Request(config["htmltags"]["base_url"]+link,meta={'dont_redirect':True,'handle_http_status_list': [301,302]},callback=self.parse_hotel)
            for i in range(config["queryparams"]["results"]):
                link = hotelsLinks[i]
                link = link[1:-1]
                link = link.split('?',1)
                yield scrapy.Request(config["htmltags"]["base_url"]+link[0],callback=self.parse_hotel)

    def parse_hotel(self,response):
        with open('config.json') as json_file:
            config = json.load(json_file)
            hotel={}
            sel = Selector(response)
            hotel['title'] = self.checkElement(1,config["htmltags"]["title"],response)
            #hotel['title']=sel.xpath(config["htmltags"]["title"]).extract_first()[1:-1]

            hotel['stars'] = self.checkElement(1,config["htmltags"]["stars"],response)
            #print(address.xpath(config["htmltags"]["addressPath"]))
            hotel['address'] = self.checkElement(1,config["htmltags"]["addressPath"],response)
            self.items.append(hotel)
 
        
    def checkElement(self,type,query,response):
        if(type==1):
            res = response.xpath(query)
            print(res)
            if(len(res)==0):
                return False
            else:
                return True
        else:
            res = response.css(query) 
            if(len(res)==0):
                return False
            else:
                return True   

                

        



