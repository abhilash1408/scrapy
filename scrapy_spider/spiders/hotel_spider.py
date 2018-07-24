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
                
                return scrapy.Request("https://www.booking.com/hotel/in/nikko.en-gb.html?checkin=2018-07-24;checkout=2018-07-26;dest_id=-2106102;dest_type=city;dist=0;group_adults=2;",callback = self.parse_hotel)
            else:
                #print(response.url)
                searchurl=self.basesearchurl+"no_rooms="+config["queryparams"]["no_rooms"]+"&group_adults="+config["queryparams"]["group_adults"]+"&group_children="+config["queryparams"]["group_children"]+"&ss="+config["queryparams"]["ss"]+"&checkin_monthday="+config["queryparams"]["checkin_monthday"]+"&checkin_month="+config["queryparams"]["checkin_month"]+"&checkin_year="+config["queryparams"]["checkin_year"]+"&checkout_monthday="+config["queryparams"]["checkout_monthday"]+"&checkout_month="+config["queryparams"]["checkout_month"]+"&checkout_year="+config["queryparams"]["checkout_year"]
                return scrapy.Request(searchurl,callback=self.parse_search)

        #searchresults.en-gb.html?city=-2106102
        #return scrapy.FormRequest.from_response(response,formxpath="//form[@id='frm']",formdata={"ss":"New Delhi","checkin_monthday":"19","checkin_month":"7","checkin_year":"2018","checkout_monthday":"22","checkout_month":"7","checkout_year":"2018" },clickdata = { "type": "submit" },callback=self.parse_search)





    def checkValidReq(self):
        with open("config.json") as con:
            config = json.load(con)

    # def parse_form(self,response):
    #     print("search completed")
    #     print(response.url)
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



    def getElement(self,sel,path):
        if(len(sel.xpath(path).extract())==0):
            return "not scraped"
        else:
            return sel.xpath(path).extract_first()

    # def getSelector(self,sel,path):
    #             if(len(sel.xpath(path).extract())==0):
    #         return "not scraped"
    #     else:
    #         return sel.xpath(path)
    def parse_hotel(self,response):
        with open("res.html","wb") as out:
                out.write(response.body)
        with open('config.json') as json_file:
            config = json.load(json_file)
            hotel={}
            sel = Selector(response)
            # print("\n\nresponse url\n\n"+response.url)
            hotel['title'] = self.getElement(sel,config["htmltags"]["title"])
            print(hotel['title'])
            #hotel['title']=sel.xpath(config["htmltags"]["title"]).extract_first()[1:-1]

            hotel['stars'] = self.getElement(sel,config["htmltags"]["stars"])
            #print(address.xpath(config["htmltags"]["addressPath"])).extract_first()[1:-1]
            hotel['address'] = self.getElement(sel,config["htmltags"]["addressPath"])

            #lst = sel.xpath("//div[contains(@id,'summary')]/p//text()").extract()
            # k=[]
            # for h in lst:
            #     k.append(h[1:-1])
            #hotel['description']=''.join(str(elem) for elem in k)
            
            hotel['description'] =self.getElement(sel,config["htmltags"]["hoteldescription"])
            # l = []
            # t=sel.xpath("//div[contains(@class,'important_facility')]/text()").extract()
            # for i in t:
            #     if i!='\n' and i not in l:
            #         i = i[1:-1]
            #         l.append(i)
            # print(l)
            # hotel['facilities'] = l
            hotel['roomtypes'] = []
            room_id=0
            rooms=sel.xpath(config["htmltags"]["roompath"])
            roomtypes_available = len(rooms)
            #print(roomtypes_available)
            if(roomtypes_available==0):
                hotel['roomtypes_available'] = 0
            for room in rooms:
                #print(room)
                valid = room.xpath(".//td")

                if(len(valid))==4 :
                    r = hotel['roomtypes'][room_id-1]
                    roo={}
                    roomtypes_available-=1
                    occupancy=room.xpath(config["htmltags"]["occupancy"])
                    roo['occupancy'] = self.getElement(occupancy,config["htmltags"]["occupancypath"])
                    price=room.xpath(config["htmltags"]["price"])
                    roo['price'] = self.getElement(price,config["htmltags"]["pricepath"])
                    conditions=room.xpath(config["htmltags"]["conditions"])
                    roo['conditions'] = []
                    t=conditions.xpath(config["htmltags"]["conditionspath1"]).css("li ::text").extract()#.css("span ::text").extract())
                    k=""
                    for i in t:
                        if i!="\n":
                            k+=i
                    roo['conditions'].append(k)
                    roo['conditions']+=conditions.xpath(config["htmltags"]["conditionspath2"]).css("span ::text").extract()
                    r['rooms'].append(roo)
                    hotel['roomtypes'][room_id-1]=r


                else:
                    room_id+=1
                    roomtype=room.xpath(config["htmltags"]["roomtype"])
                    #print(roomtype)
                    r={}
                    r['rooms'] = []
                    roo={}
                    r['room_id'] = room_id
                    #print(roomtype.xpath(".//span[contains(@class,'hprt-roomtype-icon-link')]/text()").extract_first())
                    r['roomtype'] = self.getElement(roomtype,config["htmltags"]["roomtypepath"])
                    #print(r['roomtype'])
                    r['roomdescription'] = roomtype.xpath(config["htmltags"]["roomdescription"]).extract_first()
                    facilities = roomtype.xpath(config["htmltags"]["facilities"])

                    r['facilities'] = facilities.xpath(config["htmltags"]["facilitiespath1"]).extract()
                    r['facilities']+= facilities.xpath(config["htmltags"]["facilitiespath2"]).extract()
                    r['taxinfo']=self.getElement(roomtype,config["htmltags"]["taxinfo"])
                    
                    k=roomtype.xpath(config["htmltags"]["taxinfopath"]).css("div ::text").extract() #+ roomtype.xpath(".//div[@class='hptr-taxibfo-details']/text()").extract()
                    t = []
                    for i in k:
                        if i!="\n":
                            t.append(i)
                    #print(t)

                    if(len(t)==4):
                        r['taxdetails'] =[]
                        r['taxdetails'].append( t[0]+ t[1])
                        r['taxdetails'].append(t[2]+ t[3])
                        r['available'] = True
                        #print(r)
                        
                        #r['taxrate'] = roomtype.xpath(".//div[contains(@class,'hptr-taxinfo-details')]/text()").extract_first()
                        # r['taxincluded'] = roomtype.xpath(".//span[contains(@class,'hptr-taxinfo-label--fix')]/text()").extract_first()
                    elif(len(t)==2):
                        r['taxdetails'] =[]
                        r['taxdetails'].append( t[0]+ t[1])

                                            
                        occupancy=room.xpath(config["htmltags"]["occupancy"])
                        roo['occupancy'] = occupancy.xpath(config["htmltags"]["occupancypath"]).extract_first()[1:-1]
                        price=room.xpath(config["htmltags"]["price"])
                        roo['price'] = price.xpath(config["htmltags"]["pricepath"]).extract_first()[1:-1]
                        conditions=room.xpath(config["htmltags"]["conditions"])
                        roo['conditions'] = []
                        t=conditions.xpath(config["htmltags"]["conditionspath1"]).css("li ::text").extract()#.css("span ::text").extract())
                        k=""
                        for i in t:
                            if i!="\n":
                                k+=i
                        roo['conditions'].append(k)
                        roo['conditions']+=conditions.xpath(config["htmltags"]["conditionspath2"]).css("span ::text").extract()
                        r['rooms'].append(roo)

                    else:
                        r['available'] = False
                        occupancy=room.xpath(config["htmltags"]["occupancy"])
                        roo['occupancy'] = occupancy.xpath(config["htmltags"]["occupancypath"]).extract_first()[1:-1]
                        roo['status'] = room.xpath(".//td[@colspan]//div/text()").extract_first()
                        #print(room.xpath(".//td[@colspan]//div/text()").extract())
                        r['rooms'].append(roo)




                    hotel['roomtypes'].append(r)
                    #hotel['rooms'].append(room)
            #print(hotel)


            hotel['roomtypes_available'] = roomtypes_available
            self.items.append(hotel)




                

        



