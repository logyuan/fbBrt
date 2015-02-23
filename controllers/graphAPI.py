# coding: utf-8
# try something like
import json
import time
import datetime
import jieba
import string
import re
from collections import Counter
from collections import OrderedDict
import itertools
from snownlp import SnowNLP
from snownlp import sentiment
from datetime import timedelta
from datetime import date

def test3():
    #updateCommentsDays(90, 2)
    #kowj = Page('136845026417486')
    #lien = Page('652438848137404')
    #kowj.updateInsightFromDate('2014/04/07')
    #lien.updateInsightFromDate('2014/04/07')
    text = getPageInsights('136845026417486','2014/04/07')
    text = getPageInsights('652438848137404','2014/04/07')
    return text

def clean_DB():
    rows = fbpl((fbpl.post.from_id <> '136845026417486') & (fbpl.post.from_id <> '652438848137404') ).select(fbpl.post.fid)
    fidlist=[]
    for row in rows:
        fidlist.append(row["fid"])   
    fbpl(fbpl.post_counts.fid.belongs(fidlist)).delete()
    fbpl.commit()

def HourlyUpdater():
    started_time = datetime.datetime.now()
    
    schedule = FBScheduler()
    today = datetime.datetime.today()
    date = today -timedelta(days=3)
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    todate =  datetime.datetime.strftime(today, "%Y/%m/%d")
    result = schedule.updatePagesSocialCount()
    result= schedule.updatePostsFromDate(fromdate)
    result= schedule.updatePostsSocialCount()
    
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='HourlyUpdater',started_time=started_time, ended_time=ended_time)
    fbdb.commit()
    return result

def DailyUpdater():
    started_time = datetime.datetime.now()
    schedule = FBScheduler()
    today = datetime.datetime.today()
    date = today -timedelta(days=2)
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    todate =  datetime.datetime.strftime(today, "%Y/%m/%d")
    result=schedule.updateInsightFromDate(fromdate)
    #result=schedule.getAllPostsSocialCount(fromdate, todate)
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='DailyUpdater',started_time=started_time, ended_time=ended_time)
    fbdb.commit()
    return result

def countInsights():
    started_time = datetime.datetime.now()
    today = datetime.datetime.today()
    date = today -timedelta(days=3)
    today = datetime.datetime.strftime(today, "%Y/%m/%d")
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    #result=getPostCommentsDays('136845026417486_523167771118541',  2 )
    lien = Page('652438848137404')
    lien.getPostsFromDate(fromdate)
    lien.getPostsFromDB('2014/04/07')
    lien.updateInsightFromDate(fromdate)
    lien.getAllPostsSocialCount(fromdate, today)
    kowj = Page('136845026417486')
    kowj.getPostsFromDate(fromdate)
    kowj.getPostsFromDB('2014/04/07')
    kowj.updateInsightFromDate(fromdate)
    kowj.getAllPostsSocialCount(fromdate, today)
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='countInsights',started_time=started_time, ended_time=ended_time)
    fbdb.commit()
    return "OK"

def updateAllComments():
    started_time = datetime.datetime.now()
    today = datetime.datetime.today()
    date = today -timedelta(days=4)
    today = datetime.datetime.strftime(today, "%Y/%m/%d")
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    kowj = Page('136845026417486')
    kowj.getPostsFromDate(fromdate)
    kowj.getPostsFromDB('2014/04/07')
    for p in kowj.posts:
        post = Post(p["fid"])
        post.updateComments()
        post.convertComments()

    lien = Page('652438848137404')
    lien.getPostsFromDate(fromdate)

    lien.getPostsFromDB('2014/04/07')
    for q in lien.posts:
        post2 = Post(q["fid"])
        post2.updateComments()
        post2.convertComments()

    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='updateAllComments',started_time=started_time, ended_time=ended_time)
    fbdb.commit()

def updateCommentsDays(days1, days2):
    started_time = datetime.datetime.now()
    
    today = datetime.datetime.today()
    date = today -timedelta(days=days1)
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    todate =  datetime.datetime.strftime(today, "%Y/%m/%d")
    kowj = Page('136845026417486')
    #kowj.getPostsFromDate(today)
    kowj.getPostsFromDB(fromdate)
    for p in kowj.posts:
        post = Post(p["fid"])
        post.update_and_convertCommentsDays( kowj.name , kowj.fid, post.fid, days2)


    lien = Page('652438848137404')
    #lien.getPostsFromDate(today)
    lien.getPostsFromDB(fromdate)
    for q in lien.posts:
        post2 = Post(q["fid"])
        post2.update_and_convertCommentsDays(lien.name , lien.fid, post2.fid, days2)

        
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='updateCommentsDays('+ str(days1) + ',' + str(days2) + ')',started_time=started_time, ended_time=ended_time)
    fbdb.commit()

def getPostCountFromid():
    end_time = datetime.datetime.utcnow() - timedelta(days=6)
    from_time = end_time - timedelta(days=7)
    rows = fbdb((fbdb.post_counts.date_time >= from_time) & (fbdb.post_counts.date_time < end_time)).select()
    id_dict = {}
    while len(rows) != 0:
    #try:
        for row in rows:
            fid = row.fid
            if id_dict.get(fid) == None:
                row1 = fbdb(fbdb.post.fid.like('%' + fid)).select().first()
                from_id = row1.from_id if row1 else None
                dict1 = {fid:from_id}
                id_dict.update(dict1)
            else:
                from_id = id_dict.get(fid)
            updated_time = row.updated_time
            uputcted_time_tw = date_time + timedelta(hours=8)
            row.update_record(from_id=from_id,updated_time_utc=updated_time_utc,uputcted_time_tw=uputcted_time_tw)
        end_time = from_time
        from_time = end_time - timedelta(days=7)
        rows = fbdb((fbdb.post_counts.date_time >= from_time) & (fbdb.post_counts.date_time < end_time)).select()
    #except:
    #    raise

def getPostLifetimeCount(fid):
    post = Post(fid)
    post.getlifetime_insightsDB()
    name_list = ['lifetime_shares_count', 'lifetime_likes_count', 'lifetime_comment_count', 'lifetime_likesperhour_count', 'lifetime_sharesperhour_count', 'lifetime_commentperhour_count' ]
    list_post=[]
    list_post.append(post.lifetime_shares_count)
    list_post.append(post.lifetime_likes_count)
    list_post.append(post.lifetime_comment_count)
    list_post.append(post.lifetime_likesperhour_count)
    list_post.append(post.lifetime_sharesperhour_count)
    list_post.append(post.lifetime_commentperhour_count)

    length = len(list_post)
    for i in range(0,length):
        f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/'+ fid + '_' + name_list[i] +'.csv', 'w+')
        f.write('date,post_count\n')
        length2 = len(list_post[i])
        for j in range(0,length2):
            f.write(str(list_post[i][j]["time"])  + ','  + str(list_post1[i][j]["number"])  + '\n')
        f.close()
    return "OK"

#@auth.requires_login()
def index():
    kowj = Page('136845026417486')
    lien = Page('652438848137404')
    #kowj.updateInsightFromDate('2014/04/07')
    #lien.updateInsightFromDate('2014/04/07')
    kowj.getPostsFromDB('2014/04/07')
    lien.getPostsFromDB('2014/04/07')
    kowj.getAllPostsSocialCount('2014/04/07', '2014/11/26')
    lien.getAllPostsSocialCount('2014/04/07', '2014/11/26')
    kowj.getlifetime_insights()
    lien.getlifetime_insights()

    
    
    list_kowj = kowj.lifetime_likes_tw
    list_lien = lien.lifetime_likes_tw
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/lifetime_likes_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()    
    
    list_kowj = kowj.lifetime_likes_global
    list_lien = lien.lifetime_likes_global
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/lifetime_likes_global.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()        
#-----------------------------------Daily Social Count------------------------------------------
    list_kowj = kowj.daily_people_tw
    list_lien = lien.daily_people_tw
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_people_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()    
    
    list_kowj = kowj.daily_discuss_tw
    list_lien = lien.daily_discuss_tw
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_discuss_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()  
     
    
    list_kowj = kowj.daily_newfan_tw
    list_lien = lien.daily_newfan_tw    
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_newfan_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close() 

    list_kowj = kowj.daily_shares_count
    list_lien = lien.daily_shares_count    
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_shares_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()
    
    list_kowj = kowj.daily_likes_count
    list_lien = lien.daily_likes_count    

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_likes_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()
    
    list_kowj = kowj.daily_comment_count
    list_lien = lien.daily_comment_count
    
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/daily_comment_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()    
    

    
#-----------------------------------Weekly Social Count------------------------------------------'''    
    # Weekly new page fans
    list_kowj = kowj.weekly_newfan_tw
    list_lien = lien.weekly_newfan_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_newfan_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    # Weekly people talking about the Page
    list_kowj = kowj.weekly_people_tw
    list_lien = lien.weekly_people_tw



    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_people_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    # Weekly people interacted through the Posts
    list_kowj = kowj.weekly_discuss_tw
    list_lien = lien.weekly_discuss_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_discuss_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    # Weekly people share the Posts
    list_kowj = kowj.weekly_shares_count
    list_lien = lien.weekly_shares_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_shares_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    # Weekly people liked the Posts
    list_kowj = kowj.weekly_likes_count
    list_lien = lien.weekly_likes_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_likes_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    # Weekly people commented on the Posts
    list_kowj = kowj.weekly_comment_count
    list_lien = lien.weekly_comment_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/weekly_comment_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

#-----------------------------------biWeekly Social Count------------------------------------------  
    
    
    # biWeekly people commented on the Posts
    list_kowj = kowj.biWeekly_comment_count
    list_lien = lien.biWeekly_comment_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/biWeekly_comment_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()
    
    list_kowj = kowj.biWeekly_newfan_tw
    list_lien = lien.biWeekly_newfan_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/biWeekly_newfan_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    list_kowj = kowj.biWeekly_shares_count
    list_lien = lien.biWeekly_shares_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/biWeekly_shares_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()

    list_kowj = kowj.biWeekly_likes_count
    list_lien = lien.biWeekly_likes_count    

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/biWeekly_likes_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()    
    
#-----------------------------------days28 Social Count------------------------------------------  
        
    
    list_kowj = kowj.days28_people_tw
    list_lien = lien.days28_people_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_people_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close() 
    
    list_kowj = kowj.days28_newfan_tw
    list_lien = lien.days28_newfan_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_newfan_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close() 
   
    list_kowj = kowj.days28_discuss_tw
    list_lien = lien.days28_discuss_tw

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_discuss_tw.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close() 
    
    list_kowj = kowj.days28_likes_count
    list_lien = lien.days28_likes_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_likes_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close() 

    list_kowj = kowj.days28_comment_count
    list_lien = lien.days28_comment_count

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_comment_count.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()     
    
    list_kowj = kowj.days28_people_global
    list_lien = lien.days28_people_global

    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/days28_people_global.tsv', 'w+')
    f.write('date\tkowj\tlien\n')
    length = len(list_kowj)
    for i in range(0,length):
        f.write(str(list_kowj[length-i-1]["date"]) + '\t' + str(list_kowj[length-i-1]["number"]) + '\t' + str(list_lien[length-i-1]["number"]) + '\n')
    f.close()     
    
    
    
    
    #kowj.updateInsightFromDate('2014/04/07')
    #kowj.getPostsFromDate('2014/04/07')
    #post = Post("136845026417486_486443231457662")
    #post.getlifetime_insightsDB()
    #list_post = post.lifetime_shares_count

    #kowj.getlifetime_insights_tw()

    #post.getlifetime_insights()

    #f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/post.csv', 'w+')
    #f.write('date,post_count\n')
    #length = len(list_post)

    #for i in range(0,length):
    #    f.write(str(list_post[i]["time"])  + ','  + str(list_post[i]["number"])  + '\n')
    #f.close()


    #f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/post.csv', 'w+')
    #f.write('date,post_count\n')
    #length = len(list_post)
    #for i in range(0,length):
    #    f.write(str(list_post[i]["time"]) + ',' + str(list_post[i]["number"]) + '\n')
    #f.close()
    #return dict(list_kowj=list_kowj)

    #getPageInsights('136845026417486', '2014/08/05')


    #lien.getPostsFromDate('2014/04/07')
    #lien.updateInsightFromDate('2014/04/07')

    #lien.updateSocialCount()
    #lien.updateNewPosts()
    #post_list = lien.posts
    #for item in post_list:
    #    post = Post(item["fid"])
    #    post.updateComments()
    #return str(lien.posts)
    #kowj = Page('136845026417486')


    #kowj.updateInsight()
    #kowj.updateSocialCount()
    #kowj.updateNewPosts()
    #post_list = kowj.posts
    #messages=[]
    #for item in post_list:
    #    post = Post(item["fid"])
    #    post.updateComments()
        #messages.append(post.message)
    #post=Post("136845026417486_504402186328433")
    #return lien.insights


    #list_kowj = kowj.lifetime_likes_tw
    #list_lien = lien.lifetime_likes_tw
    #list_kowj = kowj.daily_people_tw
    #list_lien = lien.daily_people_tw
    #list_kowj = kowj.biWeekly_newfan_tw
    #list_lien = lien.biWeekly_newfan_tw
    #list_kowj = kowj.weekly_people_tw
    #list_lien = lien.weekly_people_tw
    #list_kowj = kowj.days28_people_tw
    #list_lien = lien.days28_people_tw
    #list_kowj = kowj.daily_newfan_tw
    #list_lien = lien.daily_newfan_tw
    #list_kowj = kowj.weekly_newfan_tw
    #list_lien = lien.weekly_newfan_tw
    #list_kowj = kowj.days28_newfan_tw
    #list_lien = lien.days28_newfan_tw
    #list_kowj = kowj.daily_discuss_tw
    #list_lien = lien.daily_discuss_tw
    #list_kowj = kowj.weekly_discuss_tw
    #list_lien = lien.weekly_discuss_tw
    #list_kowj = kowj.days28_discuss_tw
    #list_lien = lien.days28_discuss_tw
    #list_kowj = kowj.daily_shares_count
    #list_lien = lien.daily_shares_count
    #list_kowj = kowj.weekly_shares_count
    #list_lien = lien.weekly_shares_count
    #list_kowj = kowj.biWeekly_shares_count
    #list_lien = lien.biWeekly_shares_count
    #list_kowj = kowj.daily_likes_count
    #list_lien = lien.daily_likes_count
    #list_kowj = kowj.weekly_likes_count
    #list_lien = lien.weekly_likes_count
    #list_kowj = kowj.biWeekly_likes_count
    #list_lien = lien.biWeekly_likes_count
    #list_kowj = kowj.days28_likes_count
    #list_lien = lien.days28_likes_count
    #list_kowj = kowj.weekly_comment_count
    #list_lien = lien.weekly_comment_count


    #list_kowj = kowj.days28_comment_count
    #list_lien = lien.days28_comment_count
    #list_kowj = kowj.days28_people_global
    #list_lien = lien.days28_people_global


    
    return dict(message="OK")

class FBScheduler:

    def __init__(self):
        rows = fbdb(fbdb.page.fid <> '' ).select().as_list()
        self.pages = rows
    
    def updatePostsFromDate(self, fromdate):
        for page in self.pages:
            fid = page["fid"]
            P = Page(fid)
            P.getPostsFromDate(fromdate)
        return "Success!"
    
    def updateInsightFromDate(self, fromdate):
        for page in self.pages:
            fid = page["fid"]
            P = Page(fid)
            P.updateInsightFromDate(fromdate)
        return "Success!"
    
    def updatePostsSocialCount(self):
        for page in self.pages:
            fid = page["fid"]
            P = Page(fid)
            P.getPostsFromDB("2014/11/29")
            for post in P.posts:
                Post = P.getPost(post["fid"])
                Post.updateSocialCount()
        return "Success!"
    
    def updatePagesSocialCount(self):
        for page in self.pages:
            fid = page["fid"]
            P = Page(fid)
            P.updateSocialCount()
        return "Success!"
    
    def getAllPostsSocialCount(self, fromdate, enddate):
        for page in self.pages:
            fid = page["fid"]
            P = Page(fid)
            P.getPostsFromDB('2014/11/29')
            P.getAllPostsSocialCount(fromdate,enddate)
        return "Success!"

@auth.requires_login()
def convertComms(fid):
    graph = getGraph()
    row= fbdb(fbdb.post.fid == fid).select().first()
    from_team = row['from_name']
    from_page = row['from_id']
    from_post = row['fid']
    comments_arr = row['comments_arr']
    for comment in comments_arr:
        fid = comment['id']
        com = fbdb(fbdb.comments.fid == fid).select().first()
        if com == None:
            result = getComment(fid, from_team, from_page, from_post)
            comments = result["comments"] if 'comments' in result else []
            for comm in comments:
                cid = comm['id']
                if com2 == None:
                    com2 = fbdb(fbdb.comments.fid == cid).select().first()
                    getComment(fid, from_team, from_page, from_post)
    return "ok"

@auth.requires_login()
def whole_wordcloud():
    #rows = fbdb(fbdb.comments.fid == '497419873693331_497440607024591').select()
    rows = fbdb(fbdb.comments.id <> '').select()
    stoplist = list(delZhStr)
    stoplist.extend(stopwords)
    p_wordclouds = []
    b_wordclouds = []
    g_wordclouds = []
    b_comment_count = 0
    g_comment_count = 0
    female_wordclouds=[]
    male_wordclouds=[]
    female_comment_count = 0
    male_comment_count = 0

    for row in rows:

        userid=row['from_id']
        from_team = row['from_team']
        segments= list(set(row['segment']))
        p_wordclouds2 = [i for i in segments if i not in stoplist]
        p_wordclouds.extend(p_wordclouds2)
        prow = fbdb(fbdb.people.uid == userid).select().first()

        if prow:
            if prow['gender'] == 'male':
                male_wordclouds2 = [i for i in segments if i not in stoplist]
                male_wordclouds.extend(male_wordclouds2)
                male_comment_count+=1
            elif prow['gender'] == 'female':
                female_wordclouds2 = [i for i in segments if i not in stoplist]
                female_wordclouds.extend(female_wordclouds2)
                female_comment_count+=1
            else:
                pass

        if from_team =='柯文哲':
            g_wordclouds2 = [i for i in segments if i not in stoplist]
            g_wordclouds.extend(g_wordclouds2)
            g_comment_count+=1
        else:
            b_wordclouds2 = [i for i in segments if i not in stoplist]
            b_wordclouds.extend(b_wordclouds2)
            b_comment_count+=1

    comment_count = len(rows)

    p_wordcloud = []
    b_wordcloud = []
    g_wordcloud = []
    male_wordcloud = []
    female_wordcloud = []

    for item in Counter(p_wordclouds).most_common(1000):
        p_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(b_wordclouds).most_common(500):
        b_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(g_wordclouds).most_common(500):
        g_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(male_wordclouds).most_common(500):
        male_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(female_wordclouds).most_common(500):
        female_wordcloud.append({'count': item[1] , 'value': item[0]})

    fbdb.wordcloud.insert(comment_count=comment_count, wordclouds=p_wordcloud, b_wordclouds = b_wordcloud, g_wordclouds=g_wordcloud, female_wordclouds=female_wordcloud, male_wordclouds=male_wordcloud, b_comment_count=b_comment_count, g_comment_count=g_comment_count, updated_time = datetime.datetime.now(), male_comment_count=male_comment_count, female_comment_count=female_comment_count)
    fbdb.commit()
    #return "ok"

def user_wordcloud(userid):
    rows = fbdb(fbdb.comments.from_id == userid).select()
    comment_count = len(rows)
    stoplist = list(delZhStr)
    stoplist.extend(stopwords)
    p_wordclouds = []
    b_wordclouds = []
    g_wordclouds = []
    b_comment_count = 0
    g_comment_count = 0
    for row in rows:
        from_team = row['from_team']
        segments= list(set(row['segment']))
        p_wordclouds2 = [i for i in segments if i not in stoplist]
        p_wordclouds.extend(p_wordclouds2)
        if from_team =='柯文哲':
            g_wordclouds2 = [i for i in segments if i not in stoplist]
            g_wordclouds.extend(g_wordclouds2)
            g_comment_count+=1
        else:
            b_wordclouds2 = [i for i in segments if i not in stoplist]
            b_wordclouds.extend(b_wordclouds2)
            b_comment_count+=1
    comment_count = len(rows)
    p_wordcloud = []
    b_wordcloud = []
    g_wordcloud = []
    for item in Counter(p_wordclouds).most_common():
        p_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(b_wordclouds).most_common():
        b_wordcloud.append({'count': item[1] , 'value': item[0]})
    for item in Counter(g_wordclouds).most_common():
        g_wordcloud.append({'count': item[1] , 'value': item[0]})

    prow = fbdb(fbdb.people.uid == userid).select().first()
    if prow:
        fbdb.people.update_or_insert(fbdb.people.uid == userid, comment_count=comment_count, wordcloud=p_wordcloud, b_wordclouds = b_wordcloud, g_wordclouds=g_wordcloud, b_comment_count=b_comment_count, g_comment_count=g_comment_count, updated_time = datetime.datetime.now())
        fbdb.commit()
    else:
        raise
    return "ok"


def delay():
    time.sleep(1.5)
