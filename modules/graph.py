#!/usr/bin/env python
# coding: utf8
from gluon import *
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
from gluon import current
fbdb = current.db


class Page:
    
    def __init__(self, fid):
        #initiatize the class
        row = fbdb(fbdb.page.fid == fid).select().first()
        result = ''
        if not row:
            result = getPage(fid)
            row = fbdb(fbdb.page.fid == fid).select().first()
        self.fid = row.fid
        self.cover_source = row.cover_source
        self.picture = row.picture
        self.link = row.link
        self.name = row.name
        self.likes = row.likes
        self.talking_about_count = row.talking_about_count
        self.insights = fbdb(fbdb.page_insights.fid == fid).select().as_json()
        return None


    def updateSocialCount(self): #update every 1 hour
        #use graphAPI to get the latest page's social count
        result = getPageSocialCount(self.fid)
        self.likes = result["likes"] if "likes" in result else self.likes
        self.talkink_about_count = result["talking_about_count"] if "talking_about_count" in result else self.talkink_about_count


    def getPostsFromDB(self, fromdate):
        fromdate = datetime.datetime.strptime(fromdate, "%Y/%m/%d")
        posts = fbdb((fbdb.post.from_id == self.fid) & (fbdb.post.created_time >= fromdate)).select().as_list()
        post_list=[]
        for post in posts:
            post_list.append({"fid":post["fid"], "created_time" : post["created_time"] })
        self.posts= post_list


    def getPostsFromDate(self, fromdate):
        #use graphAPi to get the newest 3 posts
        from datetime import date
        fromdate = datetime.datetime.strptime(fromdate, "%Y/%m/%d")
        now = datetime.datetime.today()
        days = (now-fromdate).days
        result = getPosts(self.fid, days)
        posts=result["postsdata"]
        post_list=[]
        for post in posts:
            post_list.append({"fid":post["id"], "created_time" : post["created_time"] })
        self.posts= post_list

    def updateNewPosts(self): #update every 1 hour
        #use graphAPi to get the newest 3 posts
        days = 1
        result = getPosts(self.fid, days)
        posts=result["data"]
        post_list=[]
        for post in posts:
            post_list.append({"fid":post["id"], "created_time" : post["created_time"] })
        self.posts= post_list

    def getPost(self, fid):
        self.post = Post(fid)
        return self.post

    def getAllPostsSocialCount(self, start_time_tw ,end_time_tw): #update every 1 hour for last two days
        end_time_tw = datetime.datetime.strptime(end_time_tw, "%Y/%m/%d")
        start_time_tw = datetime.datetime.strptime(start_time_tw, "%Y/%m/%d")
        posts=self.posts
        from_time_tw = end_time_tw-timedelta(days=1)
        shares_count = 0
        likes_count = 0
        comment_count = 0
        shares_count_next = 0
        likes_count_next = 0
        comment_count_next = 0
        daily_shares_count = 0
        daily_likes_count = 0
        daily_comment_count = 0
        total_social_count = []

        while from_time_tw >= start_time_tw:
            shares_count = 0
            likes_count = 0
            comment_count = 0
            from_time_utc = from_time_tw - timedelta(hours=8)
            end_time_utc = end_time_tw - timedelta(hours=8)
            for post in posts:
                if post["created_time"] <= end_time_utc:
                    fid = str(post["fid"].split('_')[-1])
                    #rows = fbdb(fbdb.post_counts.fid == fid).select().last()
                    row = fbdb((fbdb.post_counts.fid == fid) & (fbdb.post_counts.date_time < end_time_utc) & (fbdb.post_counts.date_time >= from_time_utc)).select().last()
                    #
                    if row != None:
                        shares_count += row.shares_count
                        likes_count += row.likes_count
                        comment_count += row.comment_count
            #return "OK"

            daily_shares_count = shares_count_next - shares_count if shares_count_next !=0 else 0
            daily_likes_count  = likes_count_next - likes_count if likes_count_next !=0 else 0
            daily_comment_count = comment_count_next - comment_count if comment_count_next !=0 else 0
            social_count={"date": end_time_tw.strftime("%Y-%m-%d"), "total_shares_count":shares_count, "total_likes_count": likes_count, "total_comment_count": comment_count, "daily_shares_count":daily_shares_count, "daily_likes_count":daily_likes_count, "daily_comment_count":daily_comment_count}
            total_social_count.append(social_count)
            row1 = fbdb((fbdb.page_insights.fid == self.fid) & (fbdb.page_insights.end_time == end_time_tw.strftime("%Y-%m-%dT07:00:00+0000"))).select().first()
            if row1 :
                row1.update_record(**fbdb.page_insights._filter_fields(social_count))
            shares_count_next = shares_count
            likes_count_next = likes_count
            comment_count_next = comment_count
            end_time_tw -= timedelta(days=1)
            from_time_tw -= timedelta(days=1)

        self.total_social_count = list(reversed(total_social_count))


    def updateInsightFromDate(self, from_date):
        #use graphAPI to get the insights info from a given date to now
        #from_date = datetime.datetime.strptime(date, "%Y/%m/%d")
        result = getPageInsights(self.fid , from_date)
        rows = fbdb(fbdb.page_insights.fid == self.fid).select()
        self.insights = rows.as_json()


    def updateInsight(self): #update everyday
        #use graphAPI to get the newest insights info within the last day
        from datetime import timedelta
        from_date = (datetime.datetime.today()-timedelta(days=1)).strftime("%Y/%m/%d")
        result = getPageInsights(self.fid, from_date)
        rows = fbdb(fbdb.page_insights.fid == self.fid).select()
        self.insights = rows.as_json()



    def getlifetime_insights(self):
        from collections import deque

        rows = fbdb(fbdb.page_insights.fid == self.fid).select()
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []
        list7 = []
        list8 = []
        list9 = []
        list10 = []
        list11 = []
        list12 = []
        list13 = []
        list14 = []
        list15 = []
        list16 = []
        list17 = []
        list18 = []
        list19 = []
        list20 = []
        list21 = []
        list22 = []
        list23 = []
        list24 = []
        list25 = []
        list26 = []
        list27 = []
        list28 = []
        list29 = []
        list30 = []



        weekStack = deque([])
        twoWeekStack = deque([])
        days28Stack = deque([])
        sharesStack= deque([])
        likesStack= deque([])
        commentStack= deque([])


        for row in rows:
            date = datetime.datetime.strftime(row.end_time_tw, '%Y%m%d')
            lifetime_likes_tw = row["lifetime_likes"].get("TW")
            daily_people_tw = row["daily_people_talking"].get("TW")
            weekly_people_tw = row["weekly_people_talking"].get("TW")
            days28_people_tw = row["days28_people_talking"].get("TW")

            lifetime_likes_global = sum(row["lifetime_likes"].values())
            daily_people_global = sum(row["daily_people_talking"].values())
            weekly_people_global = sum(row["weekly_people_talking"].values())
            days28_people_global = sum(row["days28_people_talking"].values())

            daily_shares_count = row["daily_shares_count"]
            daily_likes_count = row["daily_likes_count"]
            daily_comment_count = row["daily_comment_count"]
            total_shares_count = row["total_shares_count"]
            total_likes_count = row["total_likes_count"]
            total_comment_count = row["total_comment_count"]



            list1.append({"date": date , "number":lifetime_likes_tw})
            list2.append({"date": date , "number":daily_people_tw})
            list3.append({"date": date , "number":weekly_people_tw})
            list4.append({"date": date , "number":days28_people_tw})
            list12.append({"date": date , "number":daily_shares_count})
            list13.append({"date": date , "number":daily_likes_count})
            list14.append({"date": date , "number":daily_comment_count})
            list15.append({"date": date , "number":total_shares_count})
            list16.append({"date": date , "number":total_likes_count})
            list17.append({"date": date , "number":total_comment_count})

            list27.append({"date": date , "number":lifetime_likes_global})
            list28.append({"date": date , "number":daily_people_global})
            list29.append({"date": date , "number":weekly_people_global})
            list30.append({"date": date , "number":days28_people_global})

        self.lifetime_likes_tw = list(reversed(list1))
        self.daily_people_tw = list(reversed(list2))
        self.weekly_people_tw = list(reversed(list3))
        self.days28_people_tw = list(reversed(list4))
        self.daily_shares_count = list(reversed(list12))
        self.daily_likes_count = list(reversed(list13))
        self.daily_comment_count = list(reversed(list14))
        self.total_shares_count = list(reversed(list15))
        self.total_likes_count = list(reversed(list16))
        self.total_comment_count = list(reversed(list17))
        self.lifetime_likes_global = list(reversed(list27))
        self.daily_people_global = list(reversed(list28))
        self.weekly_people_global = list(reversed(list29))
        self.days28_people_global = list(reversed(list30))




        for lifetime, daily, weekly, days28, share, like, comment  in zip(list1, list2, list3, list4, list15, list16, list17):
            date = lifetime["date"]
            weekStack.append(lifetime["number"])
            days28Stack.append(lifetime["number"])
            twoWeekStack.append(lifetime["number"])
            sharesStack.append(share["number"])
            likesStack.append(like["number"])
            commentStack.append(comment["number"])


            M = len(days28Stack)


            if M > 28:
                days28Stack.popleft()
                sharesStack.popleft()
                likesStack.popleft()
                commentStack.popleft()
                M = len(days28Stack)


            newfansperdays28 = 0 if M < 28 else days28Stack[M-1] - days28Stack[M-28]
            sharesdays28 = 0 if M < 28 else sharesStack[M-1] - sharesStack[M-28]
            likesdays28 = 0 if M < 28 else likesStack[M-1] - likesStack[M-28]
            commentdays28 = 0 if M < 28 else commentStack[M-1] - commentStack[M-28]
            newfansbiweek = 0 if M < 14 else days28Stack[M-1] - days28Stack[M-14]
            sharesbiweek = 0 if M < 14 else sharesStack[M-1] - sharesStack[M-14]
            likesbiweek = 0 if M < 14 else likesStack[M-1] - likesStack[M-14]
            commentbiweek = 0 if M < 14 else commentStack[M-1] - commentStack[M-14]
            newfansperweek = 0 if M < 7 else days28Stack[M-1] - days28Stack[M-7]
            sharesperweek = 0 if M < 14 else sharesStack[M-1] - sharesStack[M-7]
            likesperweek = 0 if M < 14 else likesStack[M-1] - likesStack[M-7]
            commentperweek = 0 if M < 14 else commentStack[M-1] - commentStack[M-7]
            newfansperday = 0 if M < 1 else days28Stack[M-1] - days28Stack[M-2]


            daily_discuss_tw = daily["number"] - newfansperday if newfansperday != None else 0
            weekly_discuss_tw = weekly["number"] - newfansperweek if newfansperweek != None else 0
            days28_discuss_tw = days28["number"] - newfansperdays28 if newfansperdays28 != None else 0

            list5.append({"date": date , "number":newfansperday})
            list6.append({"date": date , "number":newfansperweek})
            list7.append({"date": date , "number":newfansperdays28})
            list8.append({"date": date , "number":daily_discuss_tw})
            list9.append({"date": date , "number":weekly_discuss_tw})
            list10.append({"date": date , "number":days28_discuss_tw})
            list11.append({"date": date , "number":newfansbiweek})
            list18.append({"date": date , "number":sharesdays28})
            list19.append({"date": date , "number":likesdays28})
            list20.append({"date": date , "number":commentdays28})
            list21.append({"date": date , "number":sharesbiweek})
            list22.append({"date": date , "number":likesbiweek})
            list23.append({"date": date , "number":commentbiweek})
            list24.append({"date": date , "number":sharesperweek})
            list25.append({"date": date , "number":likesperweek})
            list26.append({"date": date , "number":commentperweek})


        self.daily_newfan_tw = list5
        self.weekly_newfan_tw = list6
        self.days28_newfan_tw = list7
        self.daily_discuss_tw = list8
        self.weekly_discuss_tw = list9
        self.days28_discuss_tw = list10
        self.biWeekly_newfan_tw = list11

        self.days28_shares_count = list(reversed(list18))
        self.days28_likes_count = list(reversed(list19))
        self.days28_comment_count = list(reversed(list20))
        self.biWeekly_shares_count = list(reversed(list21))
        self.biWeekly_likes_count = list(reversed(list22))
        self.biWeekly_comment_count = list(reversed(list23))
        self.weekly_shares_count = list(reversed(list24))
        self.weekly_likes_count = list(reversed(list25))
        self.weekly_comment_count = list(reversed(list26))


        return None

    def __str__(self):
        return 'Page({0}, {1}, {2}, {3})'.format(self.name, self.fid, self.cover_source, self.link)



class Post:

    def __init__(self, fid):
        '''initiatize the class'''
        row = fbdb(fbdb.post.fid == fid).select().first()
        result = ''
        if not row:
            result = getPost(fid)
            delay()
            row = fbdb(fbdb.post.fid == fid).select().first()
        self.fid = row.fid
        self.message = row.message
        self.likes_count = row.likes_count
        self.comment_count = row.comment_count
        self.shares_count = row.shares_count
        self.ptype = row.ptype
        self.link = row.link
        self.created_time = row.created_time
        self.picture = row.picture
        self.from_id = row.from_id
        self.comments_arr=row.comments_arr
        return None


    def updateSocialCount(self): #update every 1 hour
        '''use graphAPI to get the latest post's social count'''
        result = getPostSocialCount(self.fid)
        self.likes_count = result["likes_count"] if "likes_count" in result else self.likes
        self.comment_count = result["comment_count"] if "comment_count" in result else self.talkink_about_count
        self.shares_count = result["shares_count"] if "shares_count" in result else self.checkins
        self.message =result["were_here_count"] if "were_here_count" in result else self.were_here_count

    def updateComments(self): #update every 1 hour if SocialCount changed
        '''use graphAPi to get the newest comments'''
        result = getPostComments(self.fid)
        self.comments_arr=result["comments_arr"]

    def convertComments(self):
        convertComms(self.fid)

    def getlifetime_insightsDB(self):
        rows = fbdb(fbdb.post_counts.fid == self.fid.split("_")[-1]).select()
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []

        likesthishour= 0
        likeslasthour =  0
        likesperhour = 0

        sharesthishour= 0
        shareslasthour =  0
        sharesperhour = 0

        commentthishour= 0
        commentlasthour =  0
        commentperhour = 0

        for row in rows:
            time = datetime.datetime.strftime(row.date_time+ timedelta(hours=7), '%Y%m%d%H')
            list1.append({"time": time , "number":row["shares_count"]})
            list2.append({"time": time , "number":row["likes_count"]})
            list3.append({"time": time , "number":row["comment_count"]})

            likesthishour = row["likes_count"]
            likesperhour = likesthishour - likeslasthour if likeslasthour !=0 else likesthishour
            likeslasthour = likesthishour
            list4.append({"time": time , "number":likesperhour})

            sharesthishour = row["shares_count"]
            sharesperhour = sharesthishour - shareslasthour if shareslasthour !=0 else sharesthishour
            shareslasthour = sharesthishour
            list5.append({"time": time , "number":sharesperhour})

            commentthishour = row["comment_count"]
            commentperhour = commentthishour - commentlasthour if commentlasthour !=0 else commentthishour
            commentlasthour = commentthishour
            list6.append({"time": time , "number":commentperhour})


        self.lifetime_shares_count = list1
        self.lifetime_likes_count = list2
        self.lifetime_comment_count = list3
        self.lifetime_likesperhour_count = list4
        self.lifetime_sharesperhour_count = list5
        self.lifetime_commentperhour_count = list6

        return None


    def __str__(self):
        return 'Post({0}, {1}, {2}, {3})'.format(self.fid, self.message, self.from_id, self.link)



class People:
    def __init__(self, uid):

        row = fbdb(fbdb.people.uid == uid).select().first()
        result = ''
        if not row:
            result = getPeople(uid)
            row = fbdb(fbdb.people.uid == uid).select().first()
        self.fid = row.uid
        self.name = row.name
        self.gender=row.gender
        self.locale = row.locale if 'locale' in row else None
        self.link = row.link if 'link' in row  else None
        self.picture = row.picture if 'picture' in row  else None
        self.like_count = row.like_count if 'like_count' in row  else 0
        self.b_like_count = row.b_like_count if 'b_like_count' in row  else 0
        self.g_like_count = row.g_like_count if 'g_like_count' in row  else 0
        self.comment_count = row.comment_count if 'comment_count' in row  else 0
        self.b_comment_count = row.b_comment_count if 'b_comment_count' in row else 0
        self.g_comment_count = row.g_comment_count if 'g_comment_count' in row else 0
        self.share_count = row.share_count if 'share_count' in row  else 0
        self.b_share_count = row.b_share_count if 'b_share_count' in row  else 0
        self.g_share_count = row.g_share_count if 'g_share_count' in row  else 0
        self.share_links = row.share_links if 'share_links' in row else []
        self.b_share_links = row.b_share_links if 'b_share_links' in row  else []
        self.g_share_links = row.g_share_links if 'g_share_links' in row  else []
        self.wordcloud = row.wordcloud if 'wordcloud' in row  else []
        self.b_wordclouds = row.b_wordclouds if 'b_wordclouds' in row  else []
        self.g_wordclouds = row.g_wordclouds if 'g_wordclouds' in row  else []

        return None


    def influence (self):
        influence = comment_count * 0.5
        return influence

    def __str__(self):
        return



def getPage(fid):
    graph = getGraph()
    try:
        row = fbdb(fbdb.page.fid==fid).select().first()
        if row == None:
            fb_obj = graph.request(fid ,args={'fields': 'id, name, category, checkins, about, can_post, is_published, likes, talking_about_count, were_here_count, cover, picture, link, description, cover, website'})
            name =  fb_obj["name"] if ('name' in fb_obj) else ''
            category = fb_obj["category"] if ('category' in fb_obj) else ''
            about = fb_obj["about"] if ('about' in fb_obj) else ''
            can_post = fb_obj["can_post"] if ('can_post' in fb_obj) else ''
            is_published = fb_obj["is_published"] if ('is_published' in fb_obj) else ''
            talking_about_count = fb_obj["talking_about_count"] if ('talking_about_count' in fb_obj) else ''
            link = fb_obj["link"] if ('link' in fb_obj) else ''
            likes = fb_obj["likes"] if ('likes' in fb_obj) else ''
            description = fb_obj["description"] if ('description' in fb_obj) else ''
            cover_id = fb_obj["cover"]["cover_id"] if ('cover_id' in fb_obj["cover"]) else ''
            cover_source = fb_obj["cover"]["source"] if ('source' in fb_obj["cover"]) else ''
            website = fb_obj["website"] if ('website' in fb_obj) else ''
            picture = fb_obj["picture"]["data"]["url"] if ('picture' in fb_obj) else ''
            if picture <> '':
                picture = picture.replace('_s.jpg','_n.jpg').replace('p50x50/','')
            fbdb.page.insert(fid=fid, name=name, category=category, about=about, can_post=can_post, is_published=is_published, link=link, description=description, cover_id=cover_id, cover_source=cover_source,website=website, picture=picture, talking_about_count=talking_about_count, likes=likes )
            fbdb.commit()
            delay()
            message='Successfully adding new page into the database'
    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    except:
        raise
        message=  "Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    return dict(message=message)


def getPageSocialCount(fid):
    import datetime
    from datetime import timedelta
    import time
    graph = getGraph()
    try:
        #pid = checkGraphId(oid) ' Only for Place page
        fb_obj = graph.request(fid ,args={'fields': 'id, name, talking_about_count, picture.type(large), likes'})
        likes= fb_obj["likes"] if  ('likes' in fb_obj) else 0
        talking_about_count	 = fb_obj["talking_about_count"] if  ('talking_about_count' in fb_obj) else 0
        updated_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000') #use utcnow for all purposes
        updated_time_utc = datetime.datetime.strptime(updated_time_utc,'%Y-%m-%dT%H:%M:%S+0000')
        updated_time_tw = updated_time_utc + timedelta(hours=8)
        cover_id = fb_obj["cover"]["cover_id"] if ('cover' in fb_obj) else ''
        source = fb_obj["cover"]["source"] if ('cover' in fb_obj) else ''
        picture = fb_obj["picture"]["data"]["url"] if ('picture' in fb_obj) else ''
        fbdb.page.update_or_insert(fbdb.page.fid == fid, likes=likes, updated_time_utc=updated_time_utc, updated_time_tw = updated_time_tw, talking_about_count=talking_about_count, cover_id=cover_id, source=source, picture=picture )
        fbdb.page_social_counts.insert(fid=fid, likes=likes, talking_about_count=talking_about_count, updated_time_utc=updated_time_utc, updated_time_tw=updated_time_tw)
        fbdb.commit()
        delay()
        message='Successfully update the PageSocialCount'
        return dict(message=message, talking_about_count=talking_about_count, cover_id=cover_id, source=source, picture=picture, updated_time_utc=updated_time_utc, updated_time_tw=updated_time_tw)

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)  #dict(message=str[9])


def getPosts(pageid, days):
    import time
    import datetime
    unix_timestamp  = int(time.time()) - 86400 * days
    data = []
    postsdata = []
    until = ""
    try:
        graph = getGraph()
        qtext = 'id, from, message, updated_time, created_time, status_type, type, link , picture, likes.limit(1).summary(true), shares, comments.limit(1).summary(true), object_id'
        posts_data=graph.request(pageid + '/posts', args={'fields': qtext, 'since': unix_timestamp, 'until': until, 'limit':50 })
        data = posts_data["data"]
        delay()


        while len(data) != 0:
            postsdata.extend(data)
            until = posts_data["paging"]["next"].split('&')[-1].split('until=')[-1]
            for post in data:
                fid = post["id"]
                message =  post["message"] if ('message' in post) else ''
                from_id = post["from"]["id"] if ('from' in post) else ''
                from_name = post["from"]["name"] if ('from' in post) else ''
                #from_picture = post["from"]["picture"]["data"]["url"] if ('from' in post) else ''
                created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else ''
                updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else ''
                status_type = post["status_type"] if ('status_type' in post) else ''
                ptype = post["type"] if ('type' in post) else ''
                status_type = post["status_type"] if ('status_type' in post) else ''
                link = post["link"] if ('link' in post) else ''
                picture = post["picture"] if ('picture' in post) else ''
                if picture <> '':
                    picture = picture.replace('_s.jpg','_n.jpg').replace('s130x130/','')
                shares_count = post["shares"]['count'] if ('shares' in post) else 0
                likes_count = post["likes"]["summary"]["total_count"] if ('likes' in post) else 0
                comment_count = post["comments"]["summary"]["total_count"] if ('comments' in post) else 0
                comments_arr=[]
                comments_arr = post["comments"]['data'] if ('comments' in post) else []
                object_id = post["object_id"] if ('object_id' in post) else ''

                row=fbdb(fbdb.page.fid==from_id).select().first()
                #team = row['team']
                row = fbdb(fbdb.post.fid==fid).select().first()
                if row:
                    row.update_record(message=message, object_id=object_id,ptype=ptype, status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr)
                else:
                    fbdb.post.insert(fid=fid, message=message, from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr)
                    fbdb.commit()

            posts_data=graph.request(pageid + '/posts', args={'fields': qtext, 'since': unix_timestamp, 'until': until, 'limit':50  })
            data = posts_data["data"]
            delay()

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=pageid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return dict(message=message, postsdata=postsdata)


def getPost(gid):
    graph = getGraph()
    try:
        fb_obj = graph.request(gid,args={'fields': 'id, message, updated_time, from, created_time, status_type, type, link, likes.limit(1).summary(true), shares, comments.limit(1).summary(true), object_id, picture'})
        delay()
        fid= fb_obj["id"]
        message =  fb_obj["message"] if ('message' in fb_obj) else ''
        created_time = datetime.datetime.strptime(fb_obj["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if  ('created_time' in fb_obj) else ''
        updated_time = datetime.datetime.strptime(fb_obj["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if  ('updated_time' in fb_obj) else ''
        from_id = fb_obj["from"]["id"] if ('from' in fb_obj) else ''
        from_name = fb_obj["from"]["name"] if ('from' in fb_obj) else ''
        status_type = fb_obj["status_type"] if ('status_type' in fb_obj) else ''
        ptype = fb_obj["type"] if ('type' in fb_obj) else ''
        status_type = fb_obj["status_type"] if ('status_type' in fb_obj) else ''
        link =  fb_obj["link"] if ('link' in fb_obj) else ''
        #picture =  fb_obj["picture"] if ('picture' in fb_obj) else ''
        shares_count = fb_obj["shares"]['count'] if ('shares' in fb_obj) else 0
        likes_count = fb_obj["likes"]["summary"]["total_count"] if ('summary' in fb_obj) else 0
        comment_count = fb_obj["comments"]["summary"]["total_count"] if ('summary' in fb_obj) else 0
        object_id = fb_obj["object_id"] if ('object_id' in fb_obj) else ''

        if (ptype == 'link' ) | (ptype == 'video'):
            try:
                picture =getOpengraphImage(link)
                if picture == '':
                    picture = fb_obj["picture"] if ('picture' in fb_obj) else ''
            except:
                picture = fb_obj["picture"] if ('picture' in fb_obj) else ''
        elif (ptype == 'photo' ) :
            try:
                images=[]
                images =graph.request(object_id , args={'fields':'images'})["images"]
                delay()
                for image in images:
                    if (image["height"] > 200):
                        picture = image["source"]
            except:
                picture = fb_obj["picture"] if ('picture' in fb_obj) else ''
        else:
            picture = fb_obj["picture"] if ('picture' in fb_obj) else ''


        row = fbdb(fbdb.post.fid==from_id).select().first()
        if row:
            row.update_record(fid=fid, message=message,from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count,likes_count=likes_count,comment_count=comment_count,team=team, updated_time=updated_time)
        else:
            fbdb.post.insert(fid=fid, message=message,from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count,likes_count=likes_count,comment_count=comment_count, updated_time=updated_time)
            fbdb.commit()
        message='Successfully adding new post into the database'

    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(fid=fid,date_time=datetime.datetime.utcnow(),error_msg=message)
        fbdb.commit()


    return dict(message=message)



def getPostSocialCount(fid):
    import datetime
    from datetime import timedelta
    import time
    graph = getGraph()
    try:
        #pid = checkGraphId(oid) ' Only for Place page
        fb_obj = graph.request(fid ,args={'fields': 'id, from, shares, updated_time,comments.limit(1).summary(true), message, likes.limit(1).summary(true)'})
        from_id = fb_obj["from"]["id"]
        likes_count= fb_obj["likes"]["summary"]["total_count "] if  ('summary' in fb_obj["likes"]) else 0
        shares_count = int(fb_obj["shares"]["count"]) if ('shares' in fb_obj) else 0
        comment_count = int(fb_obj["comments"]["summary"]["total_count"]) if ('comments' in fb_obj) else 0
        updated_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000') #use utcnow for all purposes
        updated_time_utc = datetime.datetime.strptime(updated_time_utc,'%Y-%m-%dT%H:%M:%S+0000')
        updated_time_tw = updated_time_utc + timedelta(hours=8)
        fbdb.post.update_or_insert(fbdb.post.fid == fid, from_id=from_id, likes_count=likes_count, updated_time_utc=updated_time_utc, updated_time_tw = updated_time_tw, shares_count=shares_count, comment_count=comment_count)
        fbdb.post_counts.insert(fid=fid, from_id=from_id, likes_count=likes_count, updated_time_utc=updated_time_utc, updated_time_tw = updated_time_tw, shares_count=shares_count, comment_count=comment_count)
        fbdb.commit()
        delay()
        message='Successfully update the PostSocialCount'
        return dict(message=message, likes_count=likes_count, updated_time_utc=updated_time_utc, updated_time_tw = updated_time_tw, shares_count=shares_count, comment_count=comment_count)

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)  #dict(message=str[9])


def getPostComments(fid):
    import datetime
    from datetime import timedelta
    import time
    graph = getGraph()
    try:
        qtext = 'id,message,comments,from,like_count,likes'
        comments_arr=[]
        data = []
        #next = ""
        after = ""
        fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':500, 'after': after })
        delay()
        data = fb_obj["data"]
        while len(data) != 0:
            comments_arr.extend(data)
            #next = fb_obj["paging"]["next"] if "next" in fb_obj["paging"] else None
            #qtext = next.split('fields=')[-1].split('&')[1] if next != None else ''
            after = fb_obj["paging"]["cursors"]["after"]
            fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':500, 'after': after })
            delay()
            data = fb_obj["data"]

        fbdb.post.update_or_insert(fbdb.post.fid == fid, comments_arr=comments_arr)
        fbdb.commit()
        message = 'Successfully update the Post Comments'
        return dict(message=message,comments_arr=comments_arr)

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return None



def getPageInsights(fid, from_date):
    import datetime
    from datetime import timedelta
    import time
    since = int(time.mktime(datetime.datetime.strptime(from_date, "%Y/%m/%d").timetuple()))
    fromdate = since
    until = int(time.time())
    graph = getGraph()
    bulk = []
    try:
        data = []
        insights=[]
        fb_obj = graph.get_object(fid + '/insights', args={'limit':30, 'pretty':0,  'suppress_http_code' : 1,'since': since, 'until':until})
        data = fb_obj["data"]
        delay()

        while until >= fromdate:
            insights.append({"data":data})
            previous = fb_obj["paging"]["previous"] if "previous" in fb_obj["paging"] else None
            since = int(previous.split('since=')[-1].split('&')[0])
            until = int(previous.split('until=')[-1])
            fb_obj = graph.request(fid + '/insights', args={'limit':30, 'pretty' :0,'since': since, 'suppress_http_code' : 1 ,'until' : until})
            data = fb_obj["data"]
            delay()

        insights = list(reversed(insights))
        for insight in insights:
            data = insight["data"]
            length = len(data[0]["values"])
            for i in range(0,length):
                end_time = data[0]["values"][i]["end_time"]
                end_time_utc = datetime.datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%S+0000')
                end_time_tw = end_time_utc + timedelta(hours=8)
                lifetime_likes = data[0]["values"][i]["value"]
                daily_people_talking = data[1]["values"][i]["value"]
                weekly_people_talking = data[2]["values"][i]["value"]
                days28_people_talking = data[3]["values"][i]["value"]
                if end_time_utc >= datetime.datetime.strptime(from_date, "%Y/%m/%d"):
                    fbdb.page_insights.update_or_insert(fid=fid, end_time = end_time,lifetime_likes=lifetime_likes, daily_people_talking=daily_people_talking, weekly_people_talking=weekly_people_talking, days28_people_talking = days28_people_talking,  end_time_utc=end_time_utc, end_time_tw=end_time_tw)
                    fbdb.commit()

        message = 'Successfully update the Post Comments'
        return dict(message=message, insights=insights)

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return None

def sharedPosts():
    graph = getGraph()
    rows= fbdb(fbdb.post.fid <> '').select()
    try:
        for row in rows:
            from_team = row['team']
            from_page = row['from_id']
            from_post = row['fid']
            if row['ptype'] != 'photo':
                post_id = row['fid'].split('_')[1]
            else:
                post_id = row['link'].split('/')[-2]
                #few(post_id)
            try:
                post_data=graph.request(post_id + '/sharedposts', args={'fields':'likes.limit(1).summary(1),comments.limit(1).summary(1),message,from,id,created_time, shares','limit':1000})
                posts = post_data['data']
                time.sleep(1.3)
                for post in posts:
                    created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else ''
                    message = post["message"] if ('message' in post) else ''
                    segment = list(jieba.cut(message))
                    cid = post["id"] if ('id' in post) else ''
                    picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
                    picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
                    from_id = post["from"]["id"] if ('from' in post) else ''
                    link = post["link"]
                    person = fbdb(fbdb.people.uid == from_id).select()
                    if not person:
                        getPeople(from_id)
                        time.sleep(1.3)
                    person = fbdb(fbdb.people.uid == from_id).select().first()
                    if person:
                        share_count = int(person['share_count'])+1 if person['share_count'] != None else 1
                        share_links = person['share_links'].append(link)
                        if from_team =='柯文哲':
                            g_share_count == int(person['g_share_count'])+1 if person['g_share_count'] != None else 1
                            g_share_links = person['g_share_links'].append(link)
                        else :
                            b_share_count == int(person['b_share_count'])+1 if person['b_share_count'] != None else 1

                        fbdb.people.update_or_insert(fbdb.people.uid == from_id, share_count=share_count)
                    else:
                        getPage(from_id)
                        time.sleep(1.3)
                    from_name = post["from"]["name"] if ('from' in post) else ''
                    likes = {}
                    likes = post["likes"]["data"] if ('likes' in post) else {}
                    comments = {}
                    comments = post["comments"]["data"] if ('comments' in post) else {}
                    like_count = post["like_count"] if ('like_count' in post) else ''
                    comment_count = post["comment_count"] if ('comment_count' in post) else ''
                    parent = post["parent"] if ('parent' in post) else {"id" : row['fid']}
                    share_count=0
                    share_count = post["shares"]["count"] if ('shares' in post) else 0
                    row1 = fbdb(fbdb.comments.fid==cid).select().first()
                    if row1:
                        row1.update_record(from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count,share_count=share_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                    else:
                        fbdb.comments.insert(fid=cid, from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, share_count=share_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                        fbdb.commit()
                    for comm in comments:
                        try:
                            cid = comm['id']
                            post=graph.request(cid, args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
                            time.sleep(1.3)
                            created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else ''
                            message = post["message"] if ('message' in post) else ''
                            segment = list(jieba.cut(message))
                            cid = post["id"] if ('id' in post) else ''
                            picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
                            from_id = post["from"]["id"] if ('from' in post) else ''
                            person = fbdb(fbdb.people.uid == from_id).select()
                            if not person:
                                getPeople(from_id)
                                time.sleep(1.3)
                            from_name = post["from"]["name"] if ('from' in post) else ''
                            likes = {}
                            likes = post["likes"]['data'] if ('likes' in post) else {}
                            comments = {}
                            comments = post["comments"]['data'] if ('comments' in post) else {}
                            like_count = post["like_count"] if ('like_count' in post) else ''
                            comment_count = post["comment_count"] if ('comment_count' in post) else ''
                            parent = post["parent"] if ('parent' in post) else ''
                            #share_count = post["share_count"]if ('share_count' in post) else ''
                            row2 = fbdb(fbdb.comments.fid==cid).select().first()
                            if row2:
                                row2.update_record(from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                            else:
                                fbdb.comments.insert(fid=cid, from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                                fbdb.commit()
                        except GraphAPIError, e:
                            raise
                            message=e.result
                            fbdb.graphAPI_Error.insert(oid=from_post,date_time=datetime.datetime.today(),error_msg=message)
                            fbdb.commit()
            except GraphAPIError, e:
                raise
                message=e.result
                fbdb.graphAPI_Error.insert(oid=from_post,date_time=datetime.datetime.today(),error_msg=message)
                fbdb.commit()
    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=from_post,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    return "ok"



def getSharedPosts(eventid):
    #eventid= '1425229754405677'
    import time
    try:
        graph = getGraph()
        posts_data=graph.request(eventid + '/sharedposts', args={'fields':'id, place, message, updated_time, from.fields(id,name,picture) , created_time, status_type, type, link,picture, likes.limit(1).summary(true), shares,  comments.limit(1000).fields(from.fields(picture,id,name), message, created_time).summary(true), object_id', 'limit':1000})
        delay()
        data = []
        data = posts_data["data"]
        Urow = fbpl(fbpl.event.eventid==eventid).select().first()
        if Urow:
            shared_count = Urow.shared_count if Urow.shared_count else 0
            shared_count_sincelastupdate = len(data) - int(shared_count) if shared_count else 0
            Urow.update_record(shared_count = len(data), shared_count_sincelastupdate=shared_count_sincelastupdate)
    except GraphAPIError, e:
        raise
        message=e.result
        fbpl.graphAPI_Error.insert(placeid=eventid,date_time=datetime.datetime.today(),error_msg=message)
        fbpl.commit()
    try:
        for post in data:
            fid = post["id"].split('_')[1]
            message =  post["message"] if ('message' in post) else ''
            from_id = post["from"]["id"] if ('from' in post) else ''
            from_name = post["from"]["name"] if ('from' in post) else ''
            from_picture = post["from"]["picture"]["data"]["url"] if ('from' in post) else ''
            created_time = post["created_time"] if ('created_time' in post) else ''
            updated_time = post["updated_time"] if ('updated_time' in post) else ''
            status_type = post["status_type"] if ('status_type' in post) else ''
            ptype = post["type"] if ('type' in post) else ''
            status_type = post["status_type"] if ('status_type' in post) else ''
            link = post["link"] if ('link' in post) else ''
            picture = post["picture"] if ('picture' in post) else ''
            shares_count = post["shares"]['count'] if ('shares' in post) else 0
            likes_count = post["likes"]["summary"]["total_count"] if ('likes' in post) else 0
            comment_count = post["comments"]["summary"]["total_count"] if ('comments' in post) else 0
            comments_arr=[]
            comments_arr = post["comments"]['data'] if ('comments' in post) else []
            object_id = post["object_id"] if ('object_id' in post) else ''
            if picture <> '':
                picture = picture.replace('_s.jpg','_n.jpg').replace('130x130/','')
            placeid = post["place"]["id"] if ('place' in post) else ''
            placename = post["place"]["name"] if ('place' in post) else ''
            if placeid != '' :
                getPlace(placeid)
                time.sleep(1)

            row = fbpl(fbpl.post.fid==fid).select().first()
            if row:
                likes_sincelastupdate = int(likes_count)-int(row.likes_count) if likes_count else 0
                shares_sincelastupdate = int(shares_count)-int(row.shares_count) if shares_count else 0
                comment_sincelastupdate = int(comment_count)-int(row.comment_count) if comment_count else 0
                row.update_record(message=message, eventid=eventid, object_id=object_id,ptype=ptype, status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, likes_sincelastupdate=likes_sincelastupdate, shares_sincelastupdate=shares_sincelastupdate, comment_sincelastupdate=comment_sincelastupdate, placeid=placeid, placename=placename, updated_time=updated_time,comments_arr=comments_arr, from_picture=from_picture)
            else:
                likes_sincelastupdate=0
                shares_sincelastupdate=0
                comment_sincelastupdate=0
                fbpl.post.insert(fid=fid, message=message,eventid=eventid, from_id=from_id, from_name=from_name, from_picture=from_picture,   created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, likes_sincelastupdate=likes_sincelastupdate, shares_sincelastupdate=shares_sincelastupdate, comment_sincelastupdate=comment_sincelastupdate, placeid=placeid, placename=placename, updated_time=updated_time,comments_arr=comments_arr)
                fbpl.commit()

        message = "all posts finished"
    except GraphAPIError, e:
        raise
        message=e.result
        fbpl.graphAPI_Error.insert(placeid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbpl.commit()


    return dict(message=message)


def getPeople(userid):
    try:
        graph = getGraph()
        posts_data=graph.request(userid, args={'fields':'id,first_name,last_name,locale,gender,link,location,name,updated_time,age_range,hometown,education,timezone,work,picture'})
        delay()
        post = {}
        post = posts_data
    except GraphAPIError, e:
        posts_data=graph.request(userid, args={'fields':'id,name,category,picture'})
        delay()
        post = {}
        post = posts_data
        uid = post["id"]
        name  = post["name"] if ('name' in post) else ''
        category  = post["category"] if ('category' in post) else ''
        picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
        link = post["link"] if ('link' in post) else ''
        website = post["website"] if ('website' in post) else ''
        row = fbdb(fbdb.people.uid==uid).select().first()
        if row:
            row.update_record(name=name, category=category, website=website, link=link, picture=picture)
        else:
            fbdb.people.insert(uid=uid, name=name, category=category, link=link, picture=picture, website=website)
            fbdb.commit()
        message=e.result
        fbdb.graphAPI_Error.insert(oid=userid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return "Not a person id"
    try:
        uid = post["id"]
        first_name =  post["first_name"] if ('first_name' in post) else ''
        last_name = post["last_name"] if ('last_name' in post) else ''
        locale  = post["locale"]if ('locale' in post) else ''
        gender  = post["gender"]if ('gender' in post) else ''
        religion  = post["religion"]if ('religion' in post) else ''
        location  = post["location"]if ('location' in post) else ''
        name  = post["name"] if ('name' in post) else ''
        website  = post["website"]if ('website' in post) else ''
        relationship_status   = post["relationship_status"]if ('relationship_status' in post) else ''
        updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else ''
        age_range  = post["age_range"]if ('age_range' in post) else ''
        hometown  = post["hometown"]if ('hometown' in post) else ''
        education  = post["education"]if ('education' in post) else ''
        timezone  = post["timezone"]if ('timezone' in post) else ''
        work  = post["work"]if ('work' in post) else ''
        email  = post["email"]if ('email' in post) else ''
        link = post["link"] if ('link' in post) else ''
        picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
        row = fbdb(fbdb.people.uid==uid).select().first()
        if row:
            row.update_record(first_name=first_name, last_name=last_name, locale=locale, gender=gender, religion=religion, location=location, name=name, website=website, relationship_status=relationship_status, updated_time=updated_time, age_range=age_range, hometown=hometown, education=education, timezone=timezone, work=work, email=email, link=link, picture=picture)
        else:
            fbdb.people.insert(uid=uid, first_name=first_name, last_name=last_name, locale=locale, gender=gender, religion=religion, location=location, name=name, website=website, relationship_status=relationship_status, updated_time=updated_time, age_range=age_range, hometown=hometown, education=education, timezone=timezone, work=work, email=email, link=link, picture=picture)
            fbdb.commit()
        message = "all posts finished"
    except GraphAPIError, e:
        #raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()


    return dict(message=message)

# this part need to be modified in the future, now only support 500 records.
def getComment(fid, from_team, from_page, from_post):
    com = fbdb(fbdb.comments.fid == fid).select().first()
    r_message = ''
    row_json = com.as_json()
    if com == None:
        try:
            post=graph.request(fid, args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
            delay()
            created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else ''
            message = post["message"] if ('message' in post) else ''
            segment = list(jieba.cut(message))
            cid = post["id"] if ('id' in post) else ''
            picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
            from_id = post["from"]["id"] if ('from' in post) else ''
            person = People(from_id)
            from_name = post["from"]["name"] if ('from' in post) else ''
            likes = []
            likes = post["likes"]['data'] if ('likes' in post) else []
            comments = []
            comments = post["comments"]['data'] if ('comments' in post) else []
            like_count = post["like_count"] if ('like_count' in post) else ''
            comment_count = post["comment_count"] if ('comment_count' in post) else ''
            parent = post["parent"] if ('parent' in post) else ''

            row1 = fbdb(fbdb.comments.fid==cid).select().first()
            if row1:
                row1.update_record(from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                r_message='successfully updated the comment'
                row_json = fbdb(fbdb.comments.fid==cid).select().first().as_json()
            else:
                fbdb.comments.insert(fid=cid, from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
                fbdb.commit()
                row_json = fbdb(fbdb.comments.fid==cid).select().first().as_json()
                r_message='successfully added the comment into DB'
        except GraphAPIError, e:
            #raise
            r_message=e.result
            fbdb.graphAPI_Error.insert(oid=cid,date_time=datetime.datetime.today(),error_msg=message)
            fbdb.commit()
        except :
            #raise
            r_message="Unexpected error:", sys.exc_info()[0]
            fbdb.graphAPI_Error.insert(oid=cid,date_time=datetime.datetime.today(),error_msg=message)
            fbdb.commit()

    return dict(message=r_message, result=row_json)



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
            result = getComment(fid, from_team, from_page, from_post)["result"]
            comments = result["comments"]["data"] if 'comments' in result else []
            for comm in comments:
                cid = comm['id']
                if com2 == None:
                    com2 = fbdb(fbdb.comments.fid == cid).select().first()
                    getComment(fid, from_team, from_page, from_post)
    return "ok"


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
