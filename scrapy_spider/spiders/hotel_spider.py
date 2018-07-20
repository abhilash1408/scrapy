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
                return scrapy.Request("https://www.booking.com/hotel/in/nikko.en-gb.html?checkin=2018-07-20;checkout=2018-07-22;dest_id=-2106102;dest_type=city;dist=0;group_adults=2;",callback = self.parse_hotel)
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
        # print("\n\n\nSearch url\n\n\n")
        # print(response.url +"\n\n\n")
        with open('search.html','wb') as out:
            out.write(response.body)
        with open('config.json') as json_file:
            config = json.load(json_file)
            sel = Selector(response)
            hotelsLinks = sel.xpath(config["htmltags"]["linkpath"]).extract()
            # i = hotelsLinks[0]
            # link = i[1:-1]
            #print(sel.css(".sr-hotel__name::text").extract_first())
            #yield scrapy.Request(config["htmltags"]["base_url"]+link,meta={'dont_redirect':True,'handle_http_status_list': [301,302]},callback=self.parse_hotel)
            for i in range(config["queryparams"]["results"]):
                link = hotelsLinks[i]
                link = link[1:-1]
                link = link.split('?',1)
                # print("\n\n\nhotel link \n\n\n" + config["htmltags"]["base_url"]+ link[0])
                yield scrapy.Request(config["htmltags"]["base_url"]+link[0],callback=self.parse_hotel)

    def parse_hotel(self,response):
        with open('config.json') as json_file:
            config = json.load(json_file)
            hotel={}
            sel = Selector(response)
            # print("\n\nresponse url\n\n"+response.url)
            hotel['title'] = self.checkElement(1,config["htmltags"]["title"],response)
            #hotel['title']=sel.xpath(config["htmltags"]["title"]).extract_first()[1:-1]

            hotel['stars'] = self.checkElement(1,config["htmltags"]["stars"],response)
            #print(address.xpath(config["htmltags"]["addressPath"])).extract_first()[1:-1]
            hotel['address'] = self.checkElement(1,config["htmltags"]["addressPath"],response)

            hotel['description'] = self.checkElement(1,"//div[contains(@id,'summary')]/p//text()",response)
            #lst = sel.xpath("//div[contains(@id,'summary')]/p//text()").extract()
            # k=[]
            # for h in lst:
            #     k.append(h[1:-1])
            #hotel['description']=''.join(str(elem) for elem in k)
            
            hotel['description'] =self.checkElement(1,"//div[contains(@class,'important_facility')]/text()",response)
            # l = []
            # t=sel.xpath("//div[contains(@class,'important_facility')]/text()").extract()
            # for i in t:
            #     if i!='\n' and i not in l:
            #         i = i[1:-1]
            #         l.append(i)
            # print(l)
            # hotel['facilities'] = l
            hotel['rooms'] = []
            rooms=sel.xpath(".//tr[contains(@class,'hprt-table-last-row')]")
            print(len(rooms))
            for room in rooms:
                print(room)
                valid = room.xpath(".//td[contains(@class,'hprt-table-cheapest-block-banner')]")
                print(valid)
                roomtype=room.xpath(".//td[contains(@class,'hprt-table-cell-roomtype')]")
                #print(roomtype)
                r={}
                print(roomtype.xpath(".//span[contains(@class,'hprt-roomtype-icon-link')]/text()").extract_first())
                r['roomtype'] = roomtype.xpath(".//span[contains(@class,'hprt-roomtype-icon-link')]/text()").extract_first()
                r['roomdescription'] = roomtype.xpath(".//p[contains(@class,'short-room-desc')]/text()").extract_first()
                facilities = roomtype.xpath(".//div[@class='hprt-facilities-block']")
                r['facilities'] = facilities.xpath(".//span[contains(@class,'hprt-facilities-facility')]/span/text()").extract()
                r['facilities']+= facilities.xpath(".//ul[@class='hprt-facilities-others']/li/span/text()").extract()
                r['taxinfo'] = roomtype.xpath(".//div[@class='hptr-taxinfo-title']/text()").extract()[1:-1]
                
                k=roomtype.xpath(".//div[@class='hptr-taxinfo-details']").css("div ::text").extract() #+ roomtype.xpath(".//div[@class='hptr-taxibfo-details']/text()").extract()
                t = []
                for i in k:
                    if i!="\n":
                        t.append(i)
                #print(t)
                r['taxincluded'] = t[0]+ t[1]
                r['taxnotincluded'] = t[2]+ t[3]
                print(r)
                
                #r['taxrate'] = roomtype.xpath(".//div[contains(@class,'hptr-taxinfo-details')]/text()").extract_first()
                # r['taxincluded'] = roomtype.xpath(".//span[contains(@class,'hptr-taxinfo-label--fix')]/text()").extract_first()


                
                
                occupancy=room.xpath(".//td[contains(@class,'hprt-table-cell-occupancy')]")
                r['occupancy'] = occupancy.xpath(".//span/text()").extract_first()[1:-1]
                price=room.xpath(".//td[contains(@class,'hprt-table-cell-price')]")
                r['price'] = price.xpath(".//span/text()").extract_first()[1:-1]
                conditions=room.xpath(".//td[contains(@class,'hprt-table-cell-conditions')]")
                r['conditions'] = []
                t=conditions.xpath(".//ul/li[contains(@class,'rt_clean_up_options')]").css("li ::text").extract()#.css("span ::text").extract())
                k=""
                for i in t:
                    if i!="\n":
                        k+=i
                r['conditions'].append(k)
                r['conditions']+=conditions.xpath(".//ul/li[contains(@class,'jq_tooltip')]").css("span ::text").extract()

                hotel['rooms'].append(r)
                #hotel['rooms'].append(room)
            print(hotel)
            with open("res.html","wb") as out:
                out.write(response.body)


            self.items.append(hotel)




        
    def checkElement(self,type,query,response):
        if(type==1):
            res = response.xpath(query)
            #print(res.extract())
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

                

        



