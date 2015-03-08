# -*- coding: utf-8 -*- 
import urllib
import json
import dateutil
import datetime
import string
import re
import itertools
from collections import Counter
from collections import OrderedDict
from dateutil import parser
from datetime import timedelta
import jieba
import jieba.analyse
import jieba.posseg as pseg
from snownlp import SnowNLP
from snownlp import sentiment
from datetime import timedelta
from operator import itemgetter
import codecs
import os

#pos_train = os.path.join(request.folder,'private','dictionary','pos.txt')
#nag_train = os.path.join(request.folder,'private','dictionary','nag.txt')
#sentiment.train(pos_train, nag_train)

#sentiment.save(os.path.join(request.folder,'private','sentiment.marshal'))

dictionary_path = os.path.join(request.folder,'private','dictionary','dict.txt.big.txt')
userdict_path = os.path.join(request.folder,'private','dictionary','userdict.txt')
stopwords_path = os.path.join(request.folder,'private','dictionary','stop_words.txt')
idf_path = os.path.join(request.folder,'private','dictionary','idf.txt.big.txt')

jieba.set_dictionary(dictionary_path)
jieba.load_userdict(userdict_path)
jieba.analyse.set_stop_words(stopwords_path)
jieba.analyse.set_idf_path(idf_path)

stopwords_file = open(stopwords_path, 'r')
stopwords = [unicode(line.strip('\n'), "utf-8") for line in stopwords_file.readlines()]


#jieba.initialize()


delEnStr = string.punctuation + ' ' + string.digits
delZhStr = u'《》（）&%￥#@！{}【】「」『』？｜，、。：；丶～　' + delEnStr.encode('utf8')



def getGraph():
    a_token = auth.settings.login_form.accessToken()
    #a_token = 'CAAFPZCO9hKHkBADB8BgiU0VnSEUC4FhNfoOh3C9OLRSDkt5XGpLiRDYYwEXcN5tZBDUZBGxqk4jqAwLfYr30Avu7RBdLgxvFY7zw0I3O3PJZA636I8Wd9olsgZBSuRzt90ZCiJKAbeEmzgaMG6mRN6GNPJWqdSFBA5B8M2DRngXQZDZD'
    return GraphAPI(a_token)

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
        posts = fbdb((fbdb.post.status_type != "") & (fbdb.post.from_id == self.fid) & (fbdb.post.created_time >= fromdate)).select().as_list()
        post_list=[]
        for post in posts:
            post_list.append({"fid":post["fid"], "created_time" : post["created_time"] })
        self.posts= post_list

    def getPostsFromDate(self, fromdate):
        import time
        #use graphAPi to get the newest 3 posts
        from datetime import date
        fromdate =str(fromdate)
        since = time.mktime(time.strptime(fromdate, '%Y/%m/%d'))-localTz()
        #fromdate = datetime.datetime.strftime(fromdate, "%Y/%m/%d")
        #fromdate = datetime.datetime.strptime(fromdate, "%Y/%m/%d")
        #now = datetime.datetime.today()
        #days = (now-fromdate).days
        result = getPostsDate(self.fid, fromdate)
        posts=result["postsdata"]
        post_list=[]
        for post in posts:
            created_timestamp = time.mktime(time.strptime(post["created_time"], '%Y-%m-%dT%H:%M:%S+0000'))
            if created_timestamp >= since:
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
        end_time_tw = end_time_tw + timedelta(hours=15)
        start_time_tw = datetime.datetime.strptime(start_time_tw, "%Y/%m/%d")
        start_time_tw = start_time_tw + timedelta(hours=15)
        posts=self.posts
        from_time_tw = end_time_tw-timedelta(days=1)
        shares_count_next = 0
        likes_count_next = 0
        comment_count_next = 0
        daily_shares_count = 0
        daily_likes_count = 0
        daily_comment_count = 0
        total_social_count = []

        while from_time_tw >= start_time_tw:
            row1 = fbdb((fbdb.page_insights.fid == self.fid) & (fbdb.page_insights.end_time == end_time_tw.strftime("%Y-%m-%dT07:00:00+0000"))).select().first()
            if row1 :
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
                social_count={"fid": self.fid, "date": end_time_tw.strftime("%Y-%m-%d"), "total_shares_count":shares_count, "total_likes_count": likes_count, "total_comment_count": comment_count, "daily_shares_count":daily_shares_count, "daily_likes_count":daily_likes_count, "daily_comment_count":daily_comment_count, "end_time_utc": end_time_utc, "end_time_tw": end_time_tw, "end_time": end_time_utc.strftime("%Y-%m-%dT07:00:00+0000")}
                total_social_count.append(social_count)

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
        
        result = getPageInsights(self.fid, from_date)
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

    def updateComments(self): #update every 1 hour if SocialCount changed
        '''use graphAPi to get the newest comments'''
        result = getPostComments(self.fid)
        self.comments_arr=result["comments_arr"]
        
    def update_and_convertCommentsDays(self, from_team, from_page, from_post, days): 
        '''use graphAPi to get the newest comments'''
        result = getPostCommentsDays(self.fid, days)
        self.comments_arr=result["comments_arr"]
        for comment in self.comments_arr:
            getComment(comment["id"], from_team, from_page, from_post)
    
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
        if row:
            self.fid = row.uid if 'uid' in row else None
            self.name = row.name if 'name' in row else None
            self.gender=row.gender if 'gender' in row else None
            self.locale = row.locale if 'locale' in row else None
            self.link = row.link if 'link' in row  else None
            self.picture = row.picture if 'picture' in row  else None
            self.first_name = row.first_name if 'first_name' in row  else None
            self.last_name = row.last_name if 'last_name' in row  else None
            self.age_range = row.age_range if 'age_range' in row  else None
            self.education = row.education if 'education' in row  else None
            self.work = row.work if 'work' in row  else None
            self.hometown = row.hometown if 'hometown' in row  else None
            self.location = row.location if 'location' in row  else None
            self.updated_time = row.updated_time if 'updated_time' in row  else None
            self.religion = row.religion if 'religion' in row  else None
            self.website = row.website if 'website' in row  else None
            self.birthday = row.birthday if 'birthday' in row  else None
            self.timezone = row.picture if 'timezone' in row  else None
            self.email = row.email if 'email' in row  else None
        else:
            self.fid = uid
            self.name = "Not existing user"
            self.gender = None
        return None

    def getPostsFromDB(self, fromdate):
        fromdate = datetime.datetime.strptime(fromdate, "%Y/%m/%d")
        posts = fbdb((fbdb.post.status_type != "") & (fbdb.post.from_id == self.fid) & (fbdb.post.created_time >= fromdate)).select().as_list()
        post_list=[]
        for post in posts:
            post_list.append({"fid":post["fid"], "created_time" : post["created_time"] })
        self.posts= post_list

    #def influence (self):
        #influence = self.comment_count * 0.5
        #return influence

    def __str__(self):
        return

class News:

    def __init__(self, href):
        if href != '':
            row = fbdb(fbdb.news.href == href).select().first()
            if not row:
                result = get_news(href)
                row = fbdb(fbdb.news.href == href).select().first()
            if row:
                self.fid = row.fid if 'fid' in row else None
                self.updated_time = row.updated_time if 'updated_time' in row else None
                self.updated_time_tw = row.updated_time if 'updated_time_tw' in row else None
                self.created_time = row.updated_time if 'created_time' in row else None
                self.created_time_tw = row.updated_time if 'created_time_tw' in row else None
                self.share_count = row.share_count if 'share_count' in row else None
                self.comment_count = row.comment_count if 'comment_count' in row else None
                self.date_time = row.date_time if 'date_time' in row else None
                self.source = row.source if 'source' in row else None
                self.summary = row.summary if 'summary' in row else None
                self.title = row.title if 'title' in row else None
                self.href = row.href if 'href' in row else None
                self.fb_url = row.fb_url if 'fb_url' in row else None
                self.photo = row.photo if 'photo' in row else None
                self.related_news = row.related_news if 'related_news' in row else None
                self.related_news_date_time = row.related_news_date_time if 'related_news_date_time' in row else None
                self.from_team = row.from_team if 'from_team' in row else None
                self.related_news_source = row.related_news_source if 'related_news_source' in row else None

        return None

    def updateSocialCount(self):
        href = self.href
        results = getUrlSocialCount(href)
        self.comment_count = results['comment_count']
        self.share_count = results['share_count']

    def getCommentsFromDB(self, fromdate):
        fromdate = datetime.datetime.strptime(fromdate, "%Y/%m/%d")
        Comments = fbdb((fbdb.news_comments.from_id == self.fid) & (fbdb.news_comments.created_time >= fromdate)).select().as_json()
        #Comments_list=[]
        #for Comment in Comments:
        #    Comments_list.append({"fid":Comment["fid"], "created_time" : Comment["created_time"] })
        self.Comments = Comments

    def updateNewComments(self):
        ids = self.fid
        from_team = self.from_team
        news_source = self.source
        href= self.href
        result = getNewsComments(ids, from_team, news_source, href)
        Comments = fbdb(fbdb.news_comments.news_fid == self.fid).select().as_json()
        self.Comments = Comments

    def getComments(self):
        Comments = fbdb(fbdb.news_comments.from_id == self.fid).select().as_json()
        self.Comments = Comments

    def convertNewsComms(self):
        convertNewsComms(self.fid)

    def __str__(self):
        return

class NewsGroup:
    def __init__(self, keyword):
        self.keyword = keyword
        self.news_count = fbdb(fbdb.news.from_team == keyword).count()
        self.urls_list = fbdb(fbdb.news.from_team == keyword).select(fbdb.news.fb_url).as_list()
        self.urls_json = fbdb(fbdb.news.from_team == keyword).select(fbdb.news.fb_url).as_json()
        self.hasComment_fids_list = fbdb((fbdb.news.from_team == keyword)&(fbdb.news.comment_count>0)).select(fbdb.news.fid).as_list()
        return None

    def updateAllSocialCount(self):
        urls = ''
        for url in self.urls_list:
            if len(urls.split(',')) >=50:
                getGroupUrlsSocialCount(urls)
                urls = ''
            urls = urls + ',' + url["fb_url"] if len(urls) <> 0 else url["fb_url"]
        getGroupUrlsSocialCount(urls)

    def updateAllComments(self):
        fids = ''
        for fid in self.hasComment_fids_list:
            if len(fids.split(',')) >=50:
                getGroupNewsComment(fids)
                fids = ''
            fids = fids + ',' + fid["fid"] if len(fids) <> 0 else fid["fid"]
        getGroupNewsComment(fids)
        return None


    def __str__(self):
        return

@auth.requires_login()
def getPage(fid):
    graph = getGraph()
    try:
        row = fbdb(fbdb.page.fid==fid).select().first()
        if row == None:
            fb_obj = graph.get_object(fid)
            name =  fb_obj["name"] if ('name' in fb_obj) else None
            category = fb_obj["category"] if ('category' in fb_obj) else None
            about = fb_obj["about"] if ('about' in fb_obj) else None
            can_post = fb_obj["can_post"] if ('can_post' in fb_obj) else None
            is_published = fb_obj["is_published"] if ('is_published' in fb_obj) else None
            talking_about_count = fb_obj["talking_about_count"] if ('talking_about_count' in fb_obj) else None
            link = fb_obj["link"] if ('link' in fb_obj) else None
            likes = fb_obj["likes"] if ('likes' in fb_obj) else None
            description = fb_obj["description"] if ('description' in fb_obj) else None
            if 'cover' in fb_obj:
                cover_id = fb_obj["cover"]["cover_id"] if ('cover_id' in fb_obj["cover"]) else None
                cover_source = fb_obj["cover"]["source"] if ('source' in fb_obj["cover"]) else None
            else:
                cover_id = ''
                cover_source = ''
            website = fb_obj["website"] if ('website' in fb_obj) else None
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

@auth.requires_login()
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
        cover_id = fb_obj["cover"]["cover_id"] if ('cover' in fb_obj) else None
        source = fb_obj["cover"]["source"] if ('cover' in fb_obj) else None
        picture = fb_obj["picture"]["data"]["url"] if ('picture' in fb_obj) else None
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

@auth.requires_login()
def getPostsDate(fid, fromdate):
    import time
    import datetime
    since = time.mktime(time.strptime(fromdate, '%Y/%m/%d'))-localTz()
    until  = int(time.time())-localTz()
    data = []
    postsdata = []

    try:
        graph = getGraph()
        qtext = 'id, from, message, updated_time, created_time, status_type, type, link, name, picture, likes.limit(1).summary(true), shares, comments.limit(1).summary(true), object_id, to, with_tags, story, application, caption, description, icon, is_hidden, message_tags, place'
        posts_data=graph.request(fid + '/posts', args={'fields': qtext, 'until': until, 'limit':50 })
        data = posts_data["data"]
        delay()


        while ((until >= since) and (len(data) <> 0)):
            postsdata.extend(data)
            until = int(posts_data["paging"]["next"].split('&until=')[-1].split('&')[0])
            for post in data:
                fid = post["id"]
                message =  unicode(post["message"]) if ('message' in post) else None
                from_id = post["from"]["id"] if ('from' in post) else None
                from_name = post["from"]["name"] if ('from' in post) else None
                #from_picture = post["from"]["picture"]["data"]["url"] if ('from' in post) else None
                created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                created_timestamp = time.mktime(time.strptime(post["created_time"], '%Y-%m-%dT%H:%M:%S+0000'))
                updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else None
                status_type = post["status_type"] if ('status_type' in post) else None
                ptype = post["type"] if ('type' in post) else None
                status_type = post["status_type"] if ('status_type' in post) else None
                link = post["link"] if ('link' in post) else None
                link_name = post["name"] if ('name' in post) else None
                picture = post["picture"] if ('picture' in post) else None
                if picture:
                    picture = picture.replace('_s.jpg','_n.jpg').replace('s130x130/','')
                shares_count = post["shares"]['count'] if ('shares' in post) else 0
                likes_count = post["likes"]["summary"]["total_count"] if ('likes' in post) else 0
                comment_count = post["comments"]["summary"]["total_count"] if ('comments' in post) else 0
                comments_arr=[]
                comments_arr = post["comments"]['data'] if ('comments' in post) else []
                object_id = post["object_id"] if ('object_id' in post) else None
                to= post["to"] if ('to' in post) else None
                with_tags= post["with_tags"] if ('with_tags' in post) else None
                story= post["story"] if ('story' in post) else None
                application = post["application"] if ('application' in post) else None
                caption = post["caption"] if ('caption' in post) else None
                description= post["description"] if ('description' in post) else None
                icon= post["icon"] if ('icon' in post) else None
                is_hidden = post["is_hidden"] if ('is_hidden' in post) else None
                message_tags= post["message_tags"] if ('message_tags' in post) else None
                if ('place' in post):
                    placeid = post["place"]["id"] if ('id' in post["place"]) else None
                    placename = post["place"]["name"] if ('name' in post["place"]) else None
                    if ('location' in post["place"]):
                        street = post["place"]["location"]["street"] if ('street' in post["place"]["location"]) else None
                        city = post["place"]["location"]["city"] if ('city' in post["place"]["location"]) else None
                        state = post["place"]["location"]["state"] if ('state' in post["place"]["location"]) else None
                        country = post["place"]["location"]["country"] if ('country' in post["place"]["location"]) else None
                        zip = post["place"]["location"]["zip"] if ('zip' in post["place"]["location"]) else None
                        longitude = post["place"]["location"]["longitude"] if ('longitude' in post["place"]["location"]) else None
                        latitude = post["place"]["location"]["latitude"] if ('latitude' in post["place"]["location"]) else None
                    getPlace(placeid)
                    delay()
                else:
                    placeid = None
                    placename = None
                    street = None
                    city = None
                    state = None
                    country = None
                    zip = None
                    longitude = None
                    latitude = None

                to= post["to"] if ('to' in post) else None
                with_tags= post["with_tags"] if ('with_tags' in post) else None

                row=fbdb(fbdb.page.fid==from_id).select().first()
                #team = row['team']
                row = fbdb(fbdb.post.fid==fid).select().first()
                if created_timestamp >= since:
                    if row:
                        row.update_record(message=message, object_id=object_id,ptype=ptype, status_type=status_type, link=link, link_name=link_name, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr, to = to, with_tags = with_tags, story = story, application = application, caption = caption, description = description, icon = icon, is_hidden = is_hidden, message_tags = message_tags, placeid = placeid, placename = placename, street = street, city = city, state = state, country = country, zip = zip, longitude = longitude, latitude = latitude)
                    else:
                        fbdb.post.insert(fid=fid, message=message, from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, link_name=link_name, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr, to = to, with_tags = with_tags, story = story, application = application, caption = caption, description = description, icon = icon, is_hidden = is_hidden, message_tags = message_tags, placeid = placeid, placename = placename, street = street, city = city, state = state, country = country, zip = zip, longitude = longitude, latitude = latitude)
                        fbdb.commit()
            try:
                posts_data=graph.request(fid + '/posts', args={'fields': qtext, 'until': until, 'limit':50  })
                data = posts_data["data"]
                delay()
            except:
                #raise
                data=[]
                message=  "Unexpected error:" + fid + '/posts?until=' + str(until), sys.exc_info()[0]
                fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
                fbdb.commit()

        message = 'finished'

    except GraphAPIError, e:
        #raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return dict(message=message, postsdata=postsdata)

@auth.requires_login()
def getPostsDays(fid, days):
    import time
    import datetime
    until  = int(time.time())
    since = until - 86400 * days
    data = []
    postsdata = []
    
    try:
        graph = getGraph()
        qtext = 'id, from, message, updated_time, created_time, status_type, type, link , picture, likes.limit(1).summary(true), shares, comments.limit(1).summary(true), object_id'
        posts_data=graph.request(fid + '/posts', args={'fields': qtext, 'until': until, 'limit':50 })
        data = posts_data["data"]
        delay()


        while until >= since:
            postsdata.extend(data)
            until = int(posts_data["paging"]["next"].split('&until=')[-1].split('&')[0])
            for post in data:
                fid = post["id"]
                message =  post["message"] if ('message' in post) else None
                from_id = post["from"]["id"] if ('from' in post) else None
                from_name = post["from"]["name"] if ('from' in post) else None
                #from_picture = post["from"]["picture"]["data"]["url"] if ('from' in post) else None
                created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else None
                status_type = post["status_type"] if ('status_type' in post) else None
                ptype = post["type"] if ('type' in post) else None
                status_type = post["status_type"] if ('status_type' in post) else None
                link = post["link"] if ('link' in post) else None
                picture = post["picture"] if ('picture' in post) else None
                if picture <> '':
                    picture = picture.replace('_s.jpg','_n.jpg').replace('s130x130/','')
                shares_count = post["shares"]['count'] if ('shares' in post) else 0
                likes_count = post["likes"]["summary"]["total_count"] if ('likes' in post) else 0
                comment_count = post["comments"]["summary"]["total_count"] if ('comments' in post) else 0
                comments_arr=[]
                comments_arr = post["comments"]['data'] if ('comments' in post) else []
                object_id = post["object_id"] if ('object_id' in post) else None

                row=fbdb(fbdb.page.fid==from_id).select().first()
                #team = row['team']
                row = fbdb(fbdb.post.fid==fid).select().first()
                if row:
                    row.update_record(message=message, object_id=object_id,ptype=ptype, status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr)
                else:
                    fbdb.post.insert(fid=fid, message=message, from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count, likes_count=likes_count, comment_count=comment_count, updated_time=updated_time,comments_arr=comments_arr)
                    fbdb.commit()

            posts_data=graph.request(fid + '/posts', args={'fields': qtext, 'until': until, 'limit':50  })
            data = posts_data["data"]
            delay()
        message = 'finished'

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return dict(message=message, postsdata=postsdata)

@auth.requires_login()
def getPost(gid):
    graph = getGraph()
    try:
        fb_obj = graph.request(gid,args={'fields': 'id, message, updated_time, from, created_time, status_type, type, link, likes.limit(1).summary(true), shares, comments.limit(5).summary(true), object_id, picture'})
        delay()
        fid= fb_obj["id"]
        message =  fb_obj["message"] if ('message' in fb_obj) else None
        created_time = datetime.datetime.strptime(fb_obj["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if  ('created_time' in fb_obj) else None
        updated_time = datetime.datetime.strptime(fb_obj["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if  ('updated_time' in fb_obj) else None
        from_id = fb_obj["from"]["id"] if ('from' in fb_obj) else None
        from_name = fb_obj["from"]["name"] if ('from' in fb_obj) else None
        status_type = fb_obj["status_type"] if ('status_type' in fb_obj) else None
        ptype = fb_obj["type"] if ('type' in fb_obj) else None
        status_type = fb_obj["status_type"] if ('status_type' in fb_obj) else None
        link =  fb_obj["link"] if ('link' in fb_obj) else None
        picture =  fb_obj["picture"] if ('picture' in fb_obj) else None
        shares_count = fb_obj["shares"]['count'] if ('shares' in fb_obj) else 0
        likes_count = fb_obj["likes"]["summary"]["total_count"] if ('summary' in fb_obj) else 0
        comment_count = fb_obj["comments"]["summary"]["total_count"] if ('summary' in fb_obj) else 0
        object_id = fb_obj["object_id"] if ('object_id' in fb_obj) else None

        if (ptype == 'link' ) | (ptype == 'video'):
            try:
                picture =getOpengraphImage(link)
                if picture == '':
                    picture = fb_obj["picture"] if ('picture' in fb_obj) else None
            except:
                picture = fb_obj["picture"] if ('picture' in fb_obj) else None
        elif (ptype == 'photo' ) :
            try:
                images=[]
                images =graph.request(object_id , args={'fields':'images'})["images"]
                delay()
                for image in images:
                    if (image["height"] > 200):
                        picture = image["source"]
            except:
                picture = fb_obj["picture"] if ('picture' in fb_obj) else None
        else:
            picture = fb_obj["picture"] if ('picture' in fb_obj) else None


        row = fbdb(fbdb.post.fid==from_id).select().first()
        if row:
            row.update_record(fid=fid, message=message,from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count,likes_count=likes_count,comment_count=comment_count,team=team, updated_time=updated_time)
        else:
            fbdb.post.insert(fid=fid, message=message,from_id=from_id, from_name=from_name, created_time=created_time,object_id=object_id,ptype=ptype,status_type=status_type, link=link, picture=picture ,shares_count=shares_count,likes_count=likes_count,comment_count=comment_count, updated_time=updated_time)
            fbdb.commit()
        message='Successfully adding new post into the database'

    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=gid,date_time=datetime.datetime.utcnow(),error_msg=message)
        fbdb.commit()


    return dict(message=message)

@auth.requires_login() # this part need to be modified in the future, now only support 500 records.
def getComment(fid, from_team, from_page, from_post):
    com = fbdb(fbdb.comments.fid == fid).select().first()
    r_message = ''
    if com == None:
        try:
            graph = getGraph()
            post=graph.request(fid, args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
            delay()
            created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
            message = post["message"] if ('message' in post) else None
            segment = list(jieba.cut(message))
            cid = post["id"] if ('id' in post) else None
            picture = post["picture"]["data"]["url"] if ('picture' in post) else None
            from_id = post["from"]["id"] if ('from' in post) else None
            if from_id:
                person = People(from_id)
            from_name = post["from"]["name"] if ('from' in post) else None
            likes = []
            likes = post["likes"]['data'] if ('likes' in post) else []
            comments = []
            comments = post["comments"]['data'] if ('comments' in post) else []
            like_count = post["like_count"] if ('like_count' in post) else None
            comment_count = post["comment_count"] if ('comment_count' in post) else None
            parent = post["parent"] if ('parent' in post) else None

            row1 = fbdb(fbdb.comments.fid==cid).select().first()
            #if row1:
            #    row1.update_record(from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
            #   r_message='successfully updated the comment'
            #   row_json = fbdb(fbdb.comments.fid==cid).select().first().as_json()
            #else:
            fbdb.comments.insert(fid=cid, from_id=from_id, from_name=from_name, message=message, created_time=created_time, picture=picture, likes=likes,  comments=comments, like_count=like_count, comment_count=comment_count, from_post=from_post, from_page=from_page, from_team=from_team, parent=parent, segment=segment )
            fbdb.commit()
            row_json = fbdb(fbdb.comments.fid==cid).select().first().as_json()
            r_message='successfully added the comment into DB'
        except GraphAPIError, e:
            #raise
            row_json = {}
            r_message=e.result
            fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
            fbdb.commit()
            
        except :
            #raise
            row_json = {}
            r_message="Unexpected error:", sys.exc_info()[0]
            fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
            fbdb.commit()
    else:
        row_json = com.as_json()
    return dict(message=r_message, result=row_json)

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
def getPostSocialCount(fid):
    import datetime
    from datetime import timedelta
    import time
    graph = getGraph()
    try:
        #pid = checkGraphId(oid) ' Only for Place page
        fb_obj = graph.request(fid ,args={'fields': 'id, from, shares, updated_time,comments.limit(1).summary(true), message, likes.limit(1).summary(true)'})
        from_id = fb_obj["from"]["id"]
        likes_count= fb_obj["likes"]["summary"]["total_count"] if  ('summary' in fb_obj["likes"]) else 0
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

@auth.requires_login()
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
        fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':200 })
        delay()
        data = fb_obj["data"]
        while len(data) != 0:
            comments_arr.extend(data)
            #next = fb_obj["paging"]["next"] if "next" in fb_obj["paging"] else None
            #qtext = next.split('fields=')[-1].split('&')[1] if next != None else None
            after = fb_obj["paging"]["cursors"]["after"]
            fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':200, 'after': after })
            delay()
            data = fb_obj["data"]

        fbdb.post.update_or_insert(fbdb.post.fid == fid, comments_arr=comments_arr)
        fbdb.commit()
        message = 'Successfully update the Post Comments'
        return dict(message=message,comments_arr=comments_arr)

    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        if message.get("error").get("code") == 2:
            delay()
            result=getPostComments(fid)
            return dict(message=message,comments_arr=result["comments_arr"])
        return dict(message=message,comments_arr=[])

    return None

@auth.requires_login()
def getPostCommentsDays(fid, days):
    #fid='652438848137404_738704049510883'
    import datetime
    from datetime import timedelta
    import time
    f_date = datetime.datetime.today()-timedelta(days=days)
    since = int(time.mktime(f_date.timetuple()))
    until = int(time.time())
    graph = getGraph()
    try:
        qtext = 'id,message,comments,from,like_count,likes'
        comments_arr=[]
        data = []
        #next = ""
        after = ""
        fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':200,'since': since, 'until':until })
        delay()
        data = fb_obj["data"]
        while len(data) != 0:
            comments_arr.extend(data)
            #next = fb_obj["paging"]["next"] if "next" in fb_obj["paging"] else None
            #qtext = next.split('fields=')[-1].split('&')[1] if next != None else None
            after = fb_obj["paging"]["cursors"]["after"]
            fb_obj = graph.request(fid + '/comments' ,args={'fields': qtext, 'limit':200,'since': since, 'until':until, 'after': after })
            delay()
            data = fb_obj["data"]

        #fbdb.post.update_or_insert(fbdb.post.fid == fid, comments_arr=comments_arr)
        #fbdb.commit()
        message = 'Successfully update the Post Comments'
        return dict(message=message,comments_arr=comments_arr)

    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        if message.get("error").get("code") == 2:
            delay()
            result=getPostCommentsDays(fid, days)
            return dict(message=message,comments_arr=result["comments_arr"])
        return dict(message=message, comments_arr=[])
    except:
        raise
        message=  "Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message,comments_arr=[])

@auth.requires_login()
def getPageInsights(fid, from_date):
    #
    #fid = '136845026417486' 
    #from_date = '2014/09/16'
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
        fb_obj = graph.request(fid + '/insights')
        data = fb_obj["data"]
        delay()

        while until >= fromdate:
            insights.append({"data":data})
            previous = fb_obj["paging"]["previous"] if "previous" in fb_obj["paging"] else None
            since = int(previous.split('since=')[-1].split('&')[0])
            until = int(previous.split('until=')[-1].split('&')[0])
            fb_obj = graph.request(fid + '/insights', args={'pretty' :0,'suppress_http_code' : 1,'since': since,'until' : until})
            data = fb_obj["data"]
            delay()

        insights = list(reversed(insights))
        for insight in insights:
            data = insight["data"]
            if data !=[]:
                length = len(data[0]["values"])
                for i in range(0,length):
                    end_time = data[0]["values"][i]["end_time"]
                    end_time_utc = datetime.datetime.strptime(end_time,'%Y-%m-%dT%H:%M:%S+0000')
                    end_time_tw = end_time_utc + timedelta(hours=8)
                    lifetime_likes = data[0]["values"][i]["value"]
                    daily_people_talking = data[1]["values"][i]["value"] if len(data[1]["values"]) > i else None
                    weekly_people_talking = data[2]["values"][i]["value"] if len(data[2]["values"]) > i else None
                    days28_people_talking = data[3]["values"][i]["value"] if len(data[3]["values"]) > i else None
                    if end_time_utc >= datetime.datetime.strptime(from_date, "%Y/%m/%d"):
                        row = fbdb((fbdb.page_insights.fid==fid)&(fbdb.page_insights.end_time==end_time)).select().first()
                        if not row:
                            fbdb.page_insights.insert(fid=fid, end_time=end_time,lifetime_likes=lifetime_likes, daily_people_talking=daily_people_talking, weekly_people_talking=weekly_people_talking, days28_people_talking = days28_people_talking,  end_time_utc=end_time_utc, end_time_tw=end_time_tw)
                            fbdb.commit()

        message = 'Successfully update the Post Comments'
        return dict(message=message, insights=insights)
        
    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return dict(message=message)

    return response.json(insights)

@auth.requires_login()
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
                    created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                    message = post["message"] if ('message' in post) else None
                    segment = list(jieba.cut(message))
                    cid = post["id"] if ('id' in post) else None
                    picture = post["picture"]["data"]["url"] if ('picture' in post) else None
                    picture = post["picture"]["data"]["url"] if ('picture' in post) else None
                    from_id = post["from"]["id"] if ('from' in post) else None
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
                    from_name = post["from"]["name"] if ('from' in post) else None
                    likes = {}
                    likes = post["likes"]["data"] if ('likes' in post) else {}
                    comments = {}
                    comments = post["comments"]["data"] if ('comments' in post) else {}
                    like_count = post["like_count"] if ('like_count' in post) else None
                    comment_count = post["comment_count"] if ('comment_count' in post) else None
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
                            created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                            message = post["message"] if ('message' in post) else None
                            segment = list(jieba.cut(message))
                            cid = post["id"] if ('id' in post) else None
                            picture = post["picture"]["data"]["url"] if ('picture' in post) else None
                            from_id = post["from"]["id"] if ('from' in post) else None
                            person = fbdb(fbdb.people.uid == from_id).select()
                            if not person:
                                getPeople(from_id)
                                time.sleep(1.3)
                            from_name = post["from"]["name"] if ('from' in post) else None
                            likes = {}
                            likes = post["likes"]['data'] if ('likes' in post) else {}
                            comments = {}
                            comments = post["comments"]['data'] if ('comments' in post) else {}
                            like_count = post["like_count"] if ('like_count' in post) else None
                            comment_count = post["comment_count"] if ('comment_count' in post) else None
                            parent = post["parent"] if ('parent' in post) else None
                            #share_count = post["share_count"]if ('share_count' in post) else None
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

@auth.requires_login()
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
            message =  post["message"] if ('message' in post) else None
            from_id = post["from"]["id"] if ('from' in post) else None
            from_name = post["from"]["name"] if ('from' in post) else None
            from_picture = post["from"]["picture"]["data"]["url"] if ('from' in post) else None
            created_time = post["created_time"] if ('created_time' in post) else None
            updated_time = post["updated_time"] if ('updated_time' in post) else None
            status_type = post["status_type"] if ('status_type' in post) else None
            ptype = post["type"] if ('type' in post) else None
            status_type = post["status_type"] if ('status_type' in post) else None
            link = post["link"] if ('link' in post) else None
            picture = post["picture"] if ('picture' in post) else None
            shares_count = post["shares"]['count'] if ('shares' in post) else 0
            likes_count = post["likes"]["summary"]["total_count"] if ('likes' in post) else 0
            comment_count = post["comments"]["summary"]["total_count"] if ('comments' in post) else 0
            comments_arr=[]
            comments_arr = post["comments"]['data'] if ('comments' in post) else []
            object_id = post["object_id"] if ('object_id' in post) else None
            if picture <> '':
                picture = picture.replace('_s.jpg','_n.jpg').replace('130x130/','')
            placeid = post["place"]["id"] if ('place' in post) else None
            placename = post["place"]["name"] if ('place' in post) else None
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

@auth.requires_login()
def Sex(uid):
    row = fbdb(fbdb.people.uid==uid).select().first()
    if not row:
        user = People(uid)
        gender = user.gender
    else:
        gender = row["gender"] if 'gender' in row else None
    return gender

@auth.requires_login()
def getPeople(userid):
    try:
        graph = getGraph()
        posts_data=graph.request(userid, args={'fields':'id,first_name,last_name,locale,gender,link,location,name,updated_time,age_range,hometown,education,timezone,work,picture'})
        delay()
        post = {}
        post = posts_data
    except GraphAPIError, e:
        message=e.result
        #fbdb.graphAPI_Error.insert(oid=userid,date_time=datetime.datetime.today(),error_msg=message)
        #fbdb.commit()
        code =message['error']['code']
        if code ==100:
            try:
                posts_data=graph.request(userid, args={'fields':'id,name,category,picture,link,website'})
                delay()
                post = {}
                post = posts_data
                uid = post["id"]
                name  = post["name"] if ('name' in post) else None
                category  = post["category"] if ('category' in post) else None
                picture = post["picture"]["data"]["url"] if ('picture' in post) else None
                link = post["link"] if ('link' in post) else None
                website = post["website"] if ('website' in post) else None
                gender = None
                fbdb.people.insert(uid=uid, name=name, category=category, link=link, picture=picture, website=website)
                fbdb.commit()
                return "add page id"

            except:
                fbdb.people.insert(uid=userid, name="unavailable user")
                message=  "Unexpected error:", sys.exc_info()[0]
                fbdb.graphAPI_Error.insert(oid=userid,date_time=datetime.datetime.today(),error_msg=message)
                fbdb.commit()
                return "unavailable user"
        
    except:
        raise
        message=  "Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=userid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return "unknown error"

    uid = post["id"]
    first_name =  post["first_name"] if ('first_name' in post) else None
    last_name = post["last_name"] if ('last_name' in post) else None
    locale  = post["locale"] if ('locale' in post) else None
    gender  = post["gender"] if ('gender' in post) else None
    religion  = post["religion"] if ('religion' in post) else None
    location  = post["location"] if ('location' in post) else None
    name  = post["name"] if ('name' in post) else None
    website  = post["website"] if ('website' in post) else None
    relationship_status   = post["relationship_status"] if ('relationship_status' in post) else None
    updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else None
    age_range  = post["age_range"] if ('age_range' in post) else None
    hometown  = post["hometown"] if ('hometown' in post) else None
    education  = post["education"] if ('education' in post) else None
    timezone  = post["timezone"] if ('timezone' in post) else None
    work  = post["work"] if ('work' in post) else None
    email  = post["email"] if ('email' in post) else None
    link = post["link"] if ('link' in post) else None
    picture = post["picture"]["data"]["url"] if ('picture' in post) else None
    fbdb.people.update_or_insert(fbdb.people.uid==uid, uid=uid, first_name=first_name, last_name=last_name, locale=locale, gender=gender, religion=religion, location=location, name=name, website=website, relationship_status=relationship_status, updated_time=updated_time, age_range=age_range, hometown=hometown, education=education, timezone=timezone, work=work, email=email, link=link, picture=picture)
    fbdb.commit()
    message = "personal data collected"
    return post
    #return dict(message=message)

@auth.requires_login()
def getPlace(gid):
    graph = getGraph()
    try:
        if gid:       
            fb_obj = graph.get_object(gid)
            id= fb_obj["id"]
            row = fbdb.place(placeid=id)
            if not row: 
                name =  fb_obj["name"]
                category = fb_obj["category"] if 'category' in fb_obj else None
                category_list =  fb_obj["category_list"] if 'category_list' in fb_obj else None
                checkins= fb_obj["checkins"] if 'checkins' in fb_obj else None
                link= fb_obj["link"] if 'link' in fb_obj else None
                old_ids = ''
                if ('location' in fb_obj):
                    zip= fb_obj["location"]["zip"] if 'zip' in fb_obj["location"] else None
                    country= fb_obj["location"]["country"] if 'country' in fb_obj["location"] else None
                    state= fb_obj["location"]["state"] if 'state' in fb_obj["location"] else None
                    street= fb_obj["location"]["street"] if 'street' in fb_obj["location"] else None
                    latitude= fb_obj["location"]["latitude"] if 'latitude' in fb_obj["location"] else None
                    longitude= fb_obj["location"]["longitude"] if 'longitude' in fb_obj["location"] else None
                else:
                    zip= None
                    country= None
                    state= None
                    street= None
                    latitude= None
                    longitude= None

                fbdb.place.insert(placeid=id,name = name,country = country,state = state,street = street,latitude=latitude,longitude=longitude,category=category,category_list=category_list,zip=zip,link=link,old_ids=old_ids)

            fbdb.commit()
            message='Successfully adding new place into the database'
        else:
            message='failure, please check your placeid!'
    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(placeid=pid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    
    
    return dict(message=message) 

def delay():
    time.sleep(1.5)

def localTz():
    import time
    if time.daylight:
        offsetHour = time.altzone
    else:
        offsetHour = time.timezone
    return offsetHour

@auth.requires_login()
def get_og_url(url):
    graph = getGraph()
    url = url.strip()
    url = url.split("://")[0] + "://" + urllib.quote(url.split("://")[1])
    try:
        result = graph.request( url,args={'fields':'og_object{id,description,title,type,url,created_time,updated_time},share,id'})
        delay()
        fid = result["og_object"]["id"] if 'og_object' in result else None
        fb_url = result["og_object"]["url"] if 'og_object' in result else None
        created_time = datetime.datetime.strptime(result["og_object"]["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if 'created_time' in result["og_object"] else None
        updated_time = datetime.datetime.strptime(result["og_object"]["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if 'updated_time' in result["og_object"] else None
        updated_time_tw = updated_time + timedelta(hours=8) if updated_time else None
        created_time_tw = created_time + timedelta(hours=8) if created_time else None
        description = result["og_object"]["description"] if 'description' in result["og_object"] else None
        title = result["og_object"]["title"] if 'title' in result["og_object"] else None
        type = result["og_object"]["type"] if 'type' in result["og_object"] else None
        if "share" in result:
            comment_count = int(result["share"]["comment_count"]) if 'comment_count' in result["share"] else None
            share_count = int(result["share"]["share_count"]) if 'share_count' in result["share"] else None
        else:
            comment_count = None
            share_count = None
    except GraphAPIError, e:
        fid = None
        fb_url = None
        created_time = None
        updated_time = None
        updated_time_tw = None
        created_time_tw = None
        description = None
        title = None
        comment_count =  None
        share_count = None
        type = None
        message = e.result
        fbdb.graphAPI_Error.insert(oid=url, date_time=datetime.datetime.today(), error_msg=message)
        fbdb.commit()

    og = {"fid":fid, "fb_url":fb_url, "updated_time_tw":updated_time_tw, "created_time_tw":created_time_tw,  "type":type, "title":title, "description":description, "comment_count":comment_count, "share_count":share_count, "updated_time":updated_time, "created_time":created_time}
    return og

@auth.requires_login()
def get_og_urls(urls):
    graph = getGraph()
    result = graph.request('',args={'ids': urls,'fields':'og_object{id,description,title,type,url,created_time,updated_time},share,id'})
    delay()
    ogs=[]
    for url,og_object in result.items():
        try:
            #url = url.split("://")[0] + "://" + urllib.quote(url.split("://")[1])
            fid = og_object["og_object"]["id"] if 'og_object' in og_object else None
            fb_url = og_object["og_object"]["url"] if 'og_object' in og_object else None
            created_time = datetime.datetime.strptime(og_object["og_object"]["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if 'created_time' in og_object["og_object"] else None
            updated_time = datetime.datetime.strptime(og_object["og_object"]["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if 'updated_time' in og_object["og_object"] else None
            updated_time_tw = updated_time + timedelta(hours=8) if updated_time else None
            created_time_tw = created_time + timedelta(hours=8) if created_time else None
            description = og_object["og_object"]["description"] if 'description' in og_object["og_object"] else None
            title = og_object["og_object"]["title"] if 'title' in og_object["og_object"] else None
            type = og_object["og_object"]["type"] if 'type' in og_object["og_object"] else None
            if "share" in og_object:
                comment_count = int(og_object["share"]["comment_count"]) if 'comment_count' in og_object["share"] else None
                share_count = int(og_object["share"]["share_count"]) if 'share_count' in og_object["share"] else None
            else:
                comment_count = None
                share_count = None
        except GraphAPIError, e:
            fid = None
            fb_url = None
            created_time = None
            updated_time = None
            updated_time_tw = None
            created_time_tw = None
            description = None
            title = None
            comment_count =  None
            share_count = None
            type = None
            message = e.result
            fbdb.graphAPI_Error.insert(oid=url, date_time=datetime.datetime.today(), error_msg=message)
            fbdb.commit()

        og = {"fid":fid, "fb_url":fb_url, "updated_time_tw":updated_time_tw, "created_time_tw":created_time_tw,  "type":type, "title":title, "description":description, "comment_count":comment_count, "share_count":share_count, "updated_time":updated_time, "created_time":created_time}
        ogs.append(og)
    return ogs

@auth.requires_login()
def getNewsComments(ids, from_team, news_source, href):
    import datetime
    graph = getGraph()
    try:
        qtext = 'id,from,message,comments.limit(1000),created_time,like_count, comment_count, can_remove,likes.limit(1000)'
        comments_arr = []
        data = []
        data_all = []
        next_p = None
        after = ""
        fb_obj = graph.request(ids + '/comments', args={'fields': qtext, 'limit': 1000})
        news_href = href
        delay()
        data = fb_obj["data"]  #if "comments" in fb_obj[ids] else fb_obj[ids]["data"]
        #if len(data) != 0:
        #    if "paging" in fb_obj:
        #        next_p = fb_obj["paging"]["next"] if "next" in fb_obj["paging"] else None
        #        after = fb_obj["paging"]["cursors"]["after"]

        while len(data) != 0:
            data_all.extend(data)
            after = fb_obj["paging"]["cursors"]["after"]
            fb_obj = graph.request(ids + '/comments', args={'fields': qtext, 'limit': 1000, 'after':after})
            delay()
            data = fb_obj["data"]
        for item in data_all:
            created_time = parser.parse(item["created_time"])
            fid = item["id"]
            from_id = item["from"]["id"] if 'from' in item else None
            if from_id <> None:
                getPeople(from_id)
            from_name = item["from"]["name"] if 'from' in item else None
            message = item["message"] if 'message' in item else None
            comments_arr.append(message)
            comment_count = item["comment_count"] if 'comment_count' in item else None
            comments = item["comments"]["data"] if 'comments' in item else None
            if comments:
                for comm in comments:
                    comments_arr.append(comm["message"])
            can_remove = item["can_remove"] if 'can_remove' in item else None
            segment = list(jieba.cut(message))
            #segment = pseg.cut(row['message'])
            like_count = item["like_count"] if 'like_count' in item else 0
            likes = []
            likes = item["likes"]["data"] if 'likes' in item else []
            for person in likes:
                uid = person["id"]
                row = fbdb(fbdb.people.uid == uid).select().first()
                result = ''
                if not row:
                    result = getPeople(uid)

            fbdb.news_comments.update_or_insert(fbdb.news_comments.fid == fid, fid=fid, from_id=from_id,
                                                from_name=from_name, message=message, comments=comments, created_time=created_time,
                                                likes=likes, like_count=like_count, comment_count=comment_count, from_team=from_team,
                                                news_source=news_source, news_href=news_href, segment=segment,
                                                news_fid=ids)
            fbdb.commit()


        message = 'Successfully update the news Comments'
        return dict(message=message, comments_arr=comments_arr)

    except GraphAPIError, e:

        message = e.result
        fbdb.graphAPI_Error.insert(oid=ids, date_time=datetime.datetime.today(), error_msg=message)
        fbdb.commit()
        if message.get("error").get("code") == 2:
            delay()
            result = getNewsComments(ids, from_team, news_source, href)
            return dict(message=message, comments_arr=result["comments_arr"])
        return dict(message=message, comments_arr=[])

    except:

        message = "Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=ids, date_time=datetime.datetime.today(), error_msg=message)
        fbdb.commit()
        return dict(message=message, comments_arr=[])

    return None

def convertNewsComms(fid):
    graph = getGraph()
    row= fbdb(fbdb.news_comments.fid == fid).select().first()
    from_team = row['from_team']
    news_source = row['news_source']
    news_href = row['news_href']
    news_fid = row['fid']
    comments_arr = row['comments']
    ffids = ''
    try:
        for comment in comments_arr:
            ffid = comment['id']
            ffids = ffid if ffids == '' else ffids + ',' + ffid
            if len(ffids.split(',')) == 50:
                results = graph.request('', args={'ids' : ffids ,'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
                ffids = ''
                delay()
                for fid,post in results.items():
                    created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                    message = post["message"] if ('message' in post) else None
                    segment = list(jieba.cut(message))
                    cid = post["id"] if ('id' in post) else None
                    from_id = post["from"]["id"] if ('from' in post) else None
                    if from_id <> None:
                        person = People(from_id)
                    from_name = post["from"]["name"] if ('from' in post) else None
                    likes = []
                    likes = post["likes"]['data'] if ('likes' in post) else []
                    for person in likes:
                        uid = person["id"]
                        row = fbdb(fbdb.people.uid == uid).select().first()
                        if not row:
                            getPeople(uid)
                    comments = post["comments"]['data'] if ('comments' in post) else None
                    like_count = post["like_count"] if ('like_count' in post) else None
                    comment_count = post["comment_count"] if ('comment_count' in post) else None
                    parent = post["parent"] if ('parent' in post) else None
                    fbdb.news_comments.update_or_insert(fbdb.news_comments.fid == cid, fid = cid, from_id = from_id, from_name = from_name, message=message, created_time = created_time, likes=likes, comments=comments, like_count=like_count, comment_count=comment_count, from_team = from_team, parent = parent, segment = segment, news_source = news_source, news_href = news_href, news_fid = news_fid)
                    fbdb.commit()
        results = graph.request('', args={'ids' : ffids ,'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
        delay()
        for fid,post in results.items():
            created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
            message = post["message"] if ('message' in post) else None
            segment = list(jieba.cut(message))
            cid = post["id"] if ('id' in post) else None
            from_id = post["from"]["id"] if ('from' in post) else None
            if from_id <> None:
                person = People(from_id)
            from_name = post["from"]["name"] if ('from' in post) else None
            likes = []
            likes = post["likes"]['data'] if ('likes' in post) else []
            for person in likes:
                uid = person["id"]
                row = fbdb(fbdb.people.uid == uid).select().first()
                if not row:
                    getPeople(uid)
            comments = post["comments"]['data'] if ('comments' in post) else None
            like_count = post["like_count"] if ('like_count' in post) else None
            comment_count = post["comment_count"] if ('comment_count' in post) else None
            parent = post["parent"] if ('parent' in post) else None
            fbdb.news_comments.update_or_insert(fbdb.news_comments.fid == cid, fid = cid, from_id = from_id, from_name = from_name, message=message, created_time = created_time, likes=likes, comments=comments, like_count=like_count, comment_count=comment_count, from_team = from_team, parent = parent, segment = segment, news_source = news_source, news_href = news_href, news_fid = news_fid)
            fbdb.commit()
    except GraphAPIError, e:
        raise
        row_json = {}
        r_message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()

    except :
        raise
        row_json = {}
        r_message="Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=fids,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()
    #post = graph.request(fid, args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
        #delay()
        #com = fbdb(fbdb.news_comments.fid == ffid).select().first()
        #if com == None:
        #    result = getNewsComment(ffid, news_source, news_href, news_fid, from_team)
        #    comments = result["comments"] if 'comments' in result else None
        #    if comments:
        #        for comm in comments:
        #            cid = comm['id']
        #            com2 = fbdb(fbdb.news_comments.fid == cid).select().first()
        #            if com2 == None:
        #                result = getNewsComment(cid,news_source, news_href, news_fid, from_team)
    return str(comments_arr)

@auth.requires_login()
def getNewsComment(fid, news_source, news_href, news_fid, from_team):
    #com = fbdb(fbdb.news_comments.fid == fid).select().first()
    r_message = ''
    #if com == None:
    try:
        graph = getGraph()
        post = graph.request(fid, args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
        delay()
        created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
        message = post["message"] if ('message' in post) else None
        segment = list(jieba.cut(message))
        cid = post["id"] if ('id' in post) else None
        from_id = post["from"]["id"] if ('from' in post) else None
        if from_id <> None:
            person = People(from_id)
        from_name = post["from"]["name"] if ('from' in post) else None
        likes = []
        likes = post["likes"]['data'] if ('likes' in post) else []
        for person in likes:
            uid = person["id"]
            row = fbdb(fbdb.people.uid == uid).select().first()
            if not row:
                getPeople(uid)

        comments = post["comments"]['data'] if ('comments' in post) else None
        like_count = post["like_count"] if ('like_count' in post) else None
        comment_count = post["comment_count"] if ('comment_count' in post) else None
        parent = post["parent"] if ('parent' in post) else None
        fbdb.news_comments.update_or_insert(fbdb.news_comments.fid == cid, fid = cid, from_id = from_id, from_name = from_name, message=message, created_time = created_time, likes=likes, comments=comments, like_count=like_count, comment_count=comment_count, from_team = from_team, parent = parent, segment = segment, news_source = news_source, news_href = news_href, news_fid = news_fid)
        fbdb.commit()
        row_json = fbdb(fbdb.news_comments.fid==cid).select().first().as_json()
        r_message='successfully added the comment into DB'
    except GraphAPIError, e:
        raise
        row_json = {}
        r_message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()

    except :
        raise
        row_json = {}
        r_message="Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()
    #else:
    #    row_json = com.as_json()
    return dict(message=r_message, result=row_json)

def getGroupNewsComment(fids):
    #com = fbdb(fbdb.news_comments.fid == fid).select().first()
    r_message = ''
    #if com == None:
    try:
        graph = getGraph()
        results = graph.request('comments/', args={'ids': fids,'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count'})
        print results
        delay()
        for fid,posts in results.items():
            row = fbdb(fbdb.news.fid == fid).select().first()
            news_source=row["source"]
            news_href=row["href"]
            news_fid=fid
            from_team=row["from_team"]
            next_p = ''

            while next_p <> None:
                try:
                    next_p = posts["paging"]["cursors"]["after"] if 'next' in posts["paging"] else None
                except:
                    next_p = None
                for post in posts["data"]:
                    created_time = datetime.datetime.strptime(post["created_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('created_time' in post) else None
                    message = post["message"] if ('message' in post) else None
                    segment = list(jieba.cut(message))
                    cid = post["id"] if ('id' in post) else None
                    from_id = post["from"]["id"] if ('from' in post) else None
                    if from_id <> None:
                        person = People(from_id)
                    from_name = post["from"]["name"] if ('from' in post) else None
                    likes = []
                    likes = post["likes"]['data'] if ('likes' in post) else []
                    for person in likes:
                        uid = person["id"]
                        row = fbdb(fbdb.people.uid == uid).select().first()
                        if not row:
                            getPeople(uid)

                    comments = post["comments"]['data'] if ('comments' in post) else None
                    like_count = post["like_count"] if ('like_count' in post) else None
                    comment_count = post["comment_count"] if ('comment_count' in post) else None
                    parent = post["parent"] if ('parent' in post) else None
                    fbdb.news_comments.update_or_insert(fbdb.news_comments.fid == cid, fid = cid, from_id = from_id, from_name = from_name, message=message, created_time = created_time, likes=likes, comments=comments, like_count=like_count, comment_count=comment_count, from_team = from_team, parent = parent, segment = segment, news_source = news_source, news_href = news_href, news_fid = news_fid)
                    fbdb.commit()
                    if comments <> None:
                        convertNewsComms(cid)
                    #row_json = fbdb(fbdb.news_comments.fid==cid).select().first().as_json()
                    r_message='successfully added the comment into DB'
                if next_p <> None:
                    posts = graph.request(news_fid + '/comments', args={'fields':'likes.limit(1000),comments.limit(1000),message,from,id,like_count,created_time,parent,comment_count','after': next_p,'limit':25})
                    print 'post=   '+ str(posts)
                    delay()


    except GraphAPIError, e:
        raise
        row_json = {}
        r_message=e.result
        fbdb.graphAPI_Error.insert(oid=fid,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()

    except :
        raise
        row_json = {}
        r_message="Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(oid=fids,date_time=datetime.datetime.today(),error_msg=r_message)
        fbdb.commit()
    #else:
    #    row_json = com.as_json()
    return dict(message=r_message)

@auth.requires_login()
def getUrlSocialCount(href):
    updated_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000') #use utcnow for all purposes
    updated_time_utc = datetime.datetime.strptime(updated_time_utc,'%Y-%m-%dT%H:%M:%S+0000')
    updated_time_tw = updated_time_utc + timedelta(hours=8)
    try:
        og = get_og_url(href)
        fid = og["fid"]
        share_count = og["share_count"]
        comment_count = og["comment_count"]
        news_href = og["fb_url"]
        row = fbdb(fbdb.news.fid == fid).select().first()
        if row:
            share_count = row["share_count"]
            comment_count = row["comment_count"]
            row.update_record(comment_count_since_lastupdate = comment_count,share_count_since_lastupdate = share_count, **og)
        fbdb.news_social_counts.insert(fid=fid, news_href=news_href, comment_count=comment_count, share_count=share_count, updated_time_utc=updated_time_utc, updated_time_tw=updated_time_tw )
        fbdb.commit()
        message = 'successfully update the UrlSocialCount'
    except GraphAPIError, e:
        #raise
        share_count=None
        comment_count=None
        message = e.result
        fbdb.graphAPI_Error.insert(oid=url, date_time=datetime.datetime.today(), error_msg=message)
        fbdb.commit()
        return dict(message=message, share_count=share_count, comment_count=comment_count)

    return dict(message=message, share_count=share_count, comment_count=comment_count)


@auth.requires_login()
def getGroupUrlsSocialCount(urls):
    updated_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000') #use utcnow for all purposes
    updated_time_utc = datetime.datetime.strptime(updated_time_utc,'%Y-%m-%dT%H:%M:%S+0000')
    updated_time_tw = updated_time_utc + timedelta(hours=8)
    ogs = get_og_urls(urls)
    for og in ogs:
        fid = og["fid"]
        share_count = og["share_count"]
        comment_count = og["comment_count"]
        news_href = og["fb_url"]
        row = fbdb(fbdb.news.fid == fid).select().first()
        if row:
            share_count_since_lastupdate = share_count-row["share_count"]
            comment_count_since_lastupdate = comment_count-row["comment_count"]
            row.update_record(comment_count_since_lastupdate = comment_count_since_lastupdate,share_count_since_lastupdate = share_count_since_lastupdate, **og)
        fbdb.news_social_counts.insert(fid=fid, news_href=news_href, comment_count=comment_count, share_count=share_count, updated_time_utc=updated_time_utc, updated_time_tw=updated_time_tw )
        fbdb.commit()
    message = 'successfully update the GroupUrlsSocialCount'


    return dict(message=message)


def get_news(href):
    try:
        updated_time_utc = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S+0000') #use utcnow for all purposes
        updated_time_utc = datetime.datetime.strptime(updated_time_utc,'%Y-%m-%dT%H:%M:%S+0000')
        updated_time_tw = updated_time_utc + timedelta(hours=8)
        href = href.strip()
        url2 = href.split("://")[0] + "://" + urllib.quote(href.split("://")[1])
        og = get_og_url(url2)
        fid = og["fid"]
        fb_url = og["fb_url"]
        share_count = og["share_count"]
        comment_count = og["comment_count"]
        created_time = og["created_time"]
        updated_time = og["updated_time"]
        title = og["title"]
        summary = og['description']
        fbdb.news.update_or_insert(fbdb.news.fid==fid, href=href, **og)
        fbdb.news_social_counts.insert(fid=fid, news_href=href, comment_count=comment_count, share_count=share_count, updated_time_utc=updated_time_utc, updated_time_tw=updated_time_tw )
        fbdb.commit()
        message='Successfully adding news into the database'
    except GraphAPIError, e:
        raise
        share_count=None
        comment_count=None
        message=e.result
        fbdb.graphAPI_Error.insert(placeid=pid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    return dict(message=message, share_count=share_count, comment_count=comment_count )

def delay():
    time.sleep(1.5)
