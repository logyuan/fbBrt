# coding: utf8
# try something like
import simplejson as json
import re
import time
import datetime
from dateutil import parser
import calendar
from collections import OrderedDict


def get_rawOffset(strtime,lat,lon):
    import urllib2
    dt = parser.parse(strtime)
    ndt=calendar.timegm(dt.timetuple())
    url = "https://maps.googleapis.com/maps/api/timezone/json?location="+lat+"," +lon +"&timestamp="+str(ndt)+"&sensor=false"
    response = urllib2.urlopen(url)
    data = json.load(response)
    rawOffset = int(data['rawOffset'])
    return rawOffset
    
def utc_time(strtime,rawOffset):
    dt = parser.parse(strtime)
    ndt=calendar.timegm(dt.timetuple())
    utctimestamp = ndt-rawOffset
    utctime = datetime.datetime.fromtimestamp(utctimestamp).strftime('%Y-%m-%dT%H:%M:%S')  #2014-04-19T20:30:00-0700
    return utctime

def index(): return dict(message="hello from ws.py")

def exportAllEvents():
    rows = fbpl(fbpl.event.id<15).select(fbpl.event.ALL, orderby=~fbpl.event.id)
    results=[]
    for row in rows:
        result = OrderedDict()
        place = fbpl(fbpl.place.placeid == row.venueid).select().first()
        if not place: place = fbpl(fbpl.place.name == row.venueid).select().first()
        website = place.website if place else ""
        if (row.start_time!='') & (row.latitude!='') & (row.longitude!=''):
            rawOffset = get_rawOffset(row.start_time,row.latitude,row.longitude)
            
            datetime_start_utc  = utc_time(row.start_time, rawOffset)
            datetime_end_utc   = utc_time(row.end_time, rawOffset)
            
        else:
            datetime_start_utc =""
            datetime_end_utc  =""
        datetime_start_local = utc_time(row.start_time, 0)
        datetime_end_local  = utc_time(row.end_time, 0)
        announce_date = utc_time(row.updated_time, 0)
        categories = []
        categories.append({
            "parent_id": None,
            "id": None,
            "name":  None if not place else place.category
                           })
        category_list=[]
        if place:
            cat = place.category_list.strip("'").strip().lstrip('|').rstrip('|')
            category_list= cat.split('|')
            for category in category_list:
                category = re.sub(r"'",'',category)
                list =category.strip('{}').split(',')
                categories.append({
            "parent_id": None,
            "id": list[0].strip("'").split(':')[1].lstrip(),
            "name": list[1].strip("'").split(':')[1].lstrip()
                           })
        else :
            pass
        p_themes = []
        p_themes.append({
            "parent_id": None,
            "id": 1000000,
            "name": "sports"
                           })
        result.update({"id": long(row.eventid)})
        result.update({"datetime_start_local": datetime_start_local})
        result.update({"datetime_end_local": datetime_end_local})
        result.update({"datetime_start_utc": datetime_start_utc })
        result.update({"datetime_end_utc": datetime_end_utc })
        result.update({"title": row.name})
        result.update({"announce_date": announce_date})
        venue = OrderedDict()
        venue.update({"city": row.city})
        venue.update({"name": row.location})
        venue.update({"address": row.street +', ' + row.city +', ' + row.state +', ' + row.zipcode})
        venue.update({"url": "https://www.facebook.com/" + row.venueid})
        venue.update({"country": row.country})
        venue.update({"links": [website]})
        venue.update({"state": row.state})
        venue.update({"postal_code": row.zipcode})
        venue.update({"latlon": {
            "lat": float(row.latitude),
            "lon": float(row.longitude)
        }})
        venue.update({"timezone": row.timezone})
        venue.update({"id": long(row.eventid)})
        result.update({"venue": venue})
        result.update({"short_title": row.name})
        result.update({"categories": categories})
        result.update({"p_themes": p_themes})
        result.update({"source": "Facebook"})
        
        performers = OrderedDict()
        performers.update({"name": None})
        performers.update({"short_name": None})
        performers.update({"url": None})
        performers.update({"type": None})
        performers.update({"image": {
                "huge": None,
                "medium": None,
                "large": None,
                "small": None
            }})
        performers.update({"id": None})
        
        result.update({"performers": [performers]})
        result.update({"url": "https://www.facebook.com/" + row.eventid})
        result.update({"reviews": {
                                    "twitter": [
                                        {}
                                    ],
                                    "cyberdiscovery": [
                                        {}
                                    ]
                       }})
        results.append(result)
        

    results = json.dumps(results, sort_keys=False,separators=(',',':'),indent=4)
    file=open('/Users/logyuan/Desktop/event_fb.JSON','w')
    file.write(results)
    file.close()
    return results
