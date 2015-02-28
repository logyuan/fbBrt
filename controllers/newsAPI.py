# coding: utf8
# try something like
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
# sentiment.train('/usr/local/lib/python2.7/site-packages/snownlp/sentiment/blue.txt', '/usr/local/lib/python2.7/site-packages/snownlp/sentiment/green.txt')
#sentiment.save('/usr/local/lib/python2.7/site-packages/snownlp/sentiment/sentiment.marshal')


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


def index():
    started_time = datetime.datetime.now()
    Brtnews24_url = "https://www.kimonolabs.com/api/47bg0pfm?apikey=22879e6cd7538eea6e95b90aa70afccc"
    Brtnews7days_url = "https://www.kimonolabs.com/api/ajldjyxq?apikey=22879e6cd7538eea6e95b90aa70afccc"
    Brtnews30days_url = "https://www.kimonolabs.com/api/5xnus1ws?apikey=22879e6cd7538eea6e95b90aa70afccc"
    Brtnews1year_url = "https://www.kimonolabs.com/api/d1shcaww?apikey=22879e6cd7538eea6e95b90aa70afccc"
    kimono_api(Brtnews30days_url, "BRT")
    

    mayor24_url = "https://www.kimonolabs.com/api/7br3eu62?apikey=22879e6cd7538eea6e95b90aa70afccc"
    mayor7days_url = "https://www.kimonolabs.com/api/863lok12?apikey=22879e6cd7538eea6e95b90aa70afccc"
    mayor30days_url = "https://www.kimonolabs.com/api/8h259vhq?apikey=22879e6cd7538eea6e95b90aa70afccc"
    mayor1year_url = "https://www.kimonolabs.com/api/cs5dtbm0?apikey=22879e6cd7538eea6e95b90aa70afccc"
    #kimono_api(mayor1year_url, "林佳龍")

    today = datetime.datetime.today()
    date = today - timedelta(days=3)
    fromdate = datetime.datetime.strftime(date, "%Y/%m/%d")
    todate = datetime.datetime.strftime(today, "%Y/%m/%d")
    #checkDBNewsComments()
    #checkDBNewsCommentsFromDate(fromdate)
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='kimono_api', started_time=started_time, ended_time=ended_time)
    fbdb.commit()
    started_time = datetime.datetime.now()
    Socialcount()
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='updateSocialcount', started_time=started_time, ended_time=ended_time)
    fbdb.commit()
    started_time = datetime.datetime.now()
    checkDBNewsComments()
    ended_time = datetime.datetime.now()
    fbdb.event_logs.insert(function='checkDBNewsComments', started_time=started_time, ended_time=ended_time)
    fbdb.commit()




    return "OK"

def test():
    result=convertNewsComms('812216578849978_812222405516062')
    return result
    #return response.json(get_og_url('http://news.ltn.com.tw/news/opinion/breakingnews/1222089'))

def test2():
    t=News("http://www.appledaily.com.tw/realtimenews/article/new/20150112/540406/")
    t.updateNewComments()
    return t.Comments


def commentsByKeywords():
    key = '%女性%'
    rows = fbdb(fbdb.news.summary.like(key)).select()
    newslist = []
    for row in rows:
        if row["fid"] != None:
            newslist.append(row["fid"])
    rows = fbdb(fbdb.news_comments.news_fid.belongs(newslist)).select()
    comments = []
    likes = []
    for row in rows:
        if row["like_count"] > 10:
            news = fbdb(fbdb.news.fid == row["news_fid"]).select().first()
            comments.append('news_title:' + row["news_fid"] + news["title"] + ' like_count:' + str(
                row["like_count"]) + ' message: ' + row["message"])
            likes.append(row["like_count"])
    likes, comments = [list(x) for x in zip(*sorted(zip(likes, comments), key=itemgetter(0), reverse=True))]

    return dict(comments=comments)

@auth.requires_login()
def Socialcount():
    rows = fbdb(fbdb.news.id <> '').select()
    for row in rows:
        news_object = News(row.href)
        news_object.updateSocialCount()

    return 'OK'

def fix_url():
    rows = fbdb(fbdb.news_comments.news_fid == None).select()
    for row in rows:
        fid = row["fid"]
        news_fid = fid.split('_')[0]
        #url = "http://" + urllib.quote(href.split("http://")[1])
        #og = get_og_url(url)
        #fid = og["fid"]
        #fb_url = og["fb_url"]

        row.update_record(news_fid=news_fid)

@auth.requires_login()
def update_socialcount():
    rows = fbdb(fbdb.news.fid <> None).select()
    test=[]
    for row in rows:
        news_object = News(row.href)
        test.append(news_object.fb_url)
        news_object.updateSocialCount()
        

    return test

def fix_seg():
    rows = fbdb(fbdb.news_comments.id <> '').select()
    for row in rows:
        message = row["message"]
        segment = list(jieba.cut(message))
        row.update_record(segment=segment)


def kimono_api(url, from_team):
    response = urllib.urlopen(url)
    data = json.load(response)
    updatedtime = parser.parse(data["lastsuccess"]) + timedelta(hours=8)
    news_array = data["results"]["collection1"]
    for news in news_array:
        date_time = news["datetime"]
        if u' 小時前' in date_time:
            hours = int(date_time.strip(u' 小時前'))
            date_time = updatedtime - timedelta(hours=hours)
        elif u' 分鐘前' in date_time:
            minutes = int(date_time.strip(u' 分鐘前'))
            date_time = updatedtime - timedelta(minutes=minutes)
        else:
            date_time = date_time.replace(u'年', '/').replace(u'月', '/').strip(u'日')
            date_time = parser.parse(date_time) + timedelta(hours=12)

        source = news["source"]
        summary = news["summary"]
        title = news["title"]["text"]
        href = news["title"]["href"]
        photo = news["photo"]["src"] if 'src' in news["photo"] else ''

        related_news = []
        related_news_date_time = []
        related_news_source = []

        # if isinstance(news["related_news_datetime"], list):
        #     for item in news["related_news_datetime"]:
        #         if u' 小時前' in item:
        #             hours = int(item.strip(u' 小時前'))
        #             item = updated_time - timedelta(hours=hours)
        #             related_news_date_time.append(item)
        #         elif u' 分鐘前' in item:
        #             minutes = int(item.strip(u' 分鐘前'))
        #             item = updated_time - timedelta(minutes=minutes)
        #             related_news_date_time.append(item)
        #         else:
        #             item = item.replace(u'年', '/').replace(u'月', '/').strip(u'日')
        #             item = parser.parse(item) + timedelta(hours=12)
        #             related_news_date_time.append(item)
        #     related_news = news["related_news"]
        #     related_news_source = news["related_news_source"]
        # elif news["related_news_datetime"] == "":
        #     pass
        # else:
        #     if u' 小時前' in news["related_news_datetime"]:
        #         hours = int(news["related_news_datetime"].strip(u' 小時前'))
        #         related_news_date_time2 = updated_time - timedelta(hours=hours)
        #     elif u' 分鐘前' in news["related_news_datetime"]:
        #         minutes = int(news["related_news_datetime"].strip(u' 分鐘前'))
        #         related_news_date_time2 = updated_time - timedelta(minutes=minutes)
        #     else:
        #         related_news_date_time2 = news["related_news_datetime"].replace(u'年', '/').replace(u'月', '/').strip(
        #             u'日')
        #         related_news_date_time2 = parser.parse(related_news_date_time2) + timedelta(hours=12)
        #
        #     related_news.append(news["related_news"])
        #     related_news_date_time.append(related_news_date_time2)
        #     related_news_source.append(news["related_news_source"])
        if href != '':
            #url = "http://" + urllib.quote(href.split("http://")[1])
            href = href.strip()
            url2 = href.split("://")[0] + "://" + urllib.quote(href.split("://")[1])
            og = get_og_url(url2)
            # fid = og["fid"]
            # fb_url = og["fb_url"]
            # created_time = og["created_time"]
            # updated_time = og["updated_time"]
            # share_count = og["share_count"]
            # comment_count = og["comment_count"]
            if og["title"] == None:
                og["title"] = title
            fbdb.news.update_or_insert(fbdb.news.href==href,from_team=from_team, href=href,summary=summary, source=source, date_time=date_time,  **og)
            # fbdb.news.update_or_insert(fbdb.news.href==href, fb_url=fb_url, href=href, created_time=created_time,updated_time=updated_time, date_time=date_time, source=source, summary=summary, title=title, photo=photo, related_news=json.dumps(related_news),
            #                  related_news_date_time=related_news_date_time,
            #                  related_news_source=json.dumps(related_news_source), from_team=from_team,
            #                  share_count=share_count, comment_count=comment_count)
            fbdb.commit()

                #getUrlSocialCount(fb_url)

    return json.dumps(data)
    #return "Success!"
    #return dict(message="hello from newsAPI.py")

def checkDBNewsCommentsFromDate(from_date):
    from_date = datetime.datetime.strptime(from_date, "%Y/%m/%d")
    rows = fbdb(fbdb.news.date_time >= from_date).select()
    for row in rows:
        ids = row["fid"]
        if ids != None:
            #ids = "http://" + urllib.quote(ids.split("http://")[1])
            from_team = row["from_team"]
            news_source = row["source"]
            getNewsComments(ids, from_team, news_source)

@auth.requires_login()
def checkDBNewsComments():
    rows = fbdb((fbdb.news.fid <> None) & (fbdb.news.comment_count > 0)).select()  #
    for row in rows:
        ids = row["fid"]
        href = row["href"]
        if ids != None:
            #ids = "http://" + urllib.quote(ids.split("http://")[1])
            from_team = row["from_team"]
            news_source = row["source"]
            getNewsComments(ids, from_team, news_source, href)

    return "Ok"

def BestComments():
    stoplist = list(delZhStr)
    stoplist.extend(stopwords)
    p_wordclouds = []
    p_wordcloud = []
    p_wordclouds2 = []

    male_wordcloud = []
    female_wordcloud = []

    male_wordclouds = []
    male_wordclouds_a = []
    male_wordclouds_n = []
    male_wordclouds_nr = []
    male_wordclouds_v = []

    female_wordclouds = []
    female_wordclouds_a = []
    female_wordclouds_n = []
    female_wordclouds_nr = []
    female_wordclouds_v = []

    male_wordcloud_a = []
    male_wordcloud_n = []
    male_wordcloud_nr = []
    male_wordcloud_v = []

    female_wordcloud_a = []
    female_wordcloud_n = []
    female_wordcloud_nr = []
    female_wordcloud_v = []

    wordcloud_a = []
    wordcloud_n = []
    wordcloud_nr = []
    wordcloud_v = []
    wordcloud_a2 = []
    wordcloud_n2 = []
    wordcloud_nr2 = []
    wordcloud_v2 = []

    now = datetime.datetime.today()
    q_time = now - timedelta(days=7)
    #rows = fbdb((fbdb.news_comments.like_count >= 1)&(fbdb.news_comments.from_team=='連勝文')&(fbdb.news_comments.created_time >=q_time)).select()
    rows = fbdb(fbdb.news_comments.id <> '').select()
    for row in rows:
        #segments = list(set(row['segment']))
        segments = pseg.cut(row['message'])
        count = row["like_count"]  #// 10
        #count= 1
        wordclouds_a = []
        wordclouds_n = []
        wordclouds_nr = []
        wordclouds_v = []
        for j in range(0, count):
            for i in segments:
                if (i.word not in stoplist):
                    p_wordclouds2.append(i.word)
                if (re.search("^a", i.flag) <> None) & (i.word not in stoplist):
                    wordclouds_a.append(i.word)
                elif (i.flag == 'n') & (i.word not in stoplist):
                    wordclouds_n.append(i.word)
                elif (i.flag == 'nr') & (i.word not in stoplist):
                    wordclouds_nr.append(i.word)
                elif (re.search("^v", i.flag) <> None) & (i.word not in stoplist):
                    wordclouds_v.append(i.word)
        p_wordclouds.extend(p_wordclouds2)
        userid = row["from_id"]
        user = fbdb(fbdb.people.uid == userid).select().first()
        sex = user['gender'] if user else None
        #likes = row['likes'] if (('likes' in row) & (row['likes'] != None) & (row['likes'] != {})) else []
        #for like in likes:
        wordcloud_a2.extend(list(set(wordclouds_a)))
        wordcloud_n2.extend(list(set(wordclouds_n)))
        wordcloud_nr2.extend(list(set(wordclouds_nr)))
        wordcloud_v2.extend(list(set(wordclouds_v)))

        if sex == 'female':
            female_wordclouds.extend(list(set(p_wordclouds2)))
            female_wordclouds_a.extend(list(set(wordclouds_a)))
            female_wordclouds_n.extend(list(set(wordclouds_n)))
            female_wordclouds_nr.extend(list(set(wordclouds_nr)))
            female_wordclouds_v.extend(list(set(wordclouds_v)))
        elif sex == 'male':
            male_wordclouds.extend(list(set(p_wordclouds2)))
            male_wordclouds_a.extend(list(set(wordclouds_a)))
            male_wordclouds_n.extend(list(set(wordclouds_n)))
            male_wordclouds_nr.extend(list(set(wordclouds_nr)))
            male_wordclouds_v.extend(list(set(wordclouds_v)))
        else:
            pass
    for item in Counter(wordcloud_a2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_a.append({'name': item[0], 'size': item[1]})
    for item in Counter(wordcloud_n2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_n.append({'name': item[0], 'size': item[1]})
    for item in Counter(wordcloud_nr2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_nr.append({'name': item[0], 'size': item[1]})
    for item in Counter(wordcloud_v2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_v.append({'name': item[0], 'size': item[1]})

    for item in Counter(female_wordclouds).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud.append({'name': item[0], 'size': item[1]})
    for item in Counter(male_wordclouds).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud.append({'name': item[0], 'size': item[1]})

    list_a_female100 = []
    list_n_female100 = []
    list_nr_female100 = []
    list_v_female100 = []

    for item in Counter(female_wordclouds_a).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_a.append({'name': item[0], 'size': item[1]})
        list_a_female100.append(item[0])

    for item in Counter(female_wordclouds_n).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_n.append({'name': item[0], 'size': item[1]})
        list_n_female100.append(item[0])

    for item in Counter(female_wordclouds_nr).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_nr.append({'name': item[0], 'size': item[1]})
        list_nr_female100.append(item[0])

    for item in Counter(female_wordclouds_v).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_v.append({'name': item[0], 'size': item[1]})
        list_v_female100.append(item[0])

    list_a_male100 = []
    list_n_male100 = []
    list_nr_male100 = []
    list_v_male100 = []

    for item in Counter(male_wordclouds_a).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_a.append({'name': item[0], 'size': item[1]})
        list_a_male100.append(item[0])

    for item in Counter(male_wordclouds_n).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_n.append({'name': item[0], 'size': item[1]})
        list_n_male100.append(item[0])

    for item in Counter(male_wordclouds_nr).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_nr.append({'name': item[0], 'size': item[1]})
        list_nr_male100.append(item[0])

    for item in Counter(male_wordclouds_v).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_v.append({'name': item[0], 'size': item[1]})
        list_v_male100.append(item[0])

    female_wordcloud_a_special = []
    female_wordcloud_n_special = []
    female_wordcloud_nr_special = []
    female_wordcloud_v_special = []

    for item in Counter(female_wordclouds_a).most_common(100):
        if item[0] not in list_a_male100:
            female_wordcloud_a_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(female_wordclouds_n).most_common(100):
        if item[0] not in list_n_male100:
            female_wordcloud_n_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(female_wordclouds_nr).most_common(100):
        if item[0] not in list_nr_male100:
            female_wordcloud_nr_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(female_wordclouds_v).most_common(100):
        if item[0] not in list_v_male100:
            female_wordcloud_v_special.append({'name': item[0], 'size': item[1]})

    male_wordcloud_a_special = []
    male_wordcloud_n_special = []
    male_wordcloud_nr_special = []
    male_wordcloud_v_special = []

    for item in Counter(male_wordclouds_a).most_common(100):
        if item[0] not in list_a_female100:
            male_wordcloud_a_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(male_wordclouds_n).most_common(100):
        if item[0] not in list_n_female100:
            male_wordcloud_n_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(male_wordclouds_nr).most_common(100):
        if item[0] not in list_nr_female100:
            male_wordcloud_nr_special.append({'name': item[0], 'size': item[1]})

    for item in Counter(male_wordclouds_v).most_common(100):
        if item[0] not in list_v_female100:
            male_wordcloud_v_special.append({'name': item[0], 'size': item[1]})

    flare = {}
    flare = {"name": "flare", "children": [{"name": "female_wordcloud",
                                            "children": [{"name": "adj", "children": female_wordcloud_a_special},
                                                         {"name": "v", "children": female_wordcloud_v_special},
                                                         {"name": "nr", "children": female_wordcloud_nr_special},
                                                         {"name": "n", "children": female_wordcloud_n_special}]}]}

    f = open(os.path.join(request.folder,'private','d3','BestComments_female.json'), 'w+')
    f.write(json.dumps(flare, sort_keys=False, separators=(',', ':'), indent=4))
    f.close()
    flare = {}
    flare = {"name": "flare", "children": [{"name": "male_wordcloud",
                                            "children": [{"name": "adj", "children": male_wordcloud_a_special},
                                                         {"name": "v", "children": male_wordcloud_v_special},
                                                         {"name": "nr", "children": male_wordcloud_nr_special},
                                                         {"name": "n", "children": male_wordcloud_n_special}]}]}
    f = open(os.path.join(request.folder,'private','d3','BestComments_male.json'), 'w+')
    f.write(json.dumps(flare, sort_keys=False, separators=(',', ':'), indent=4))
    f.close()

    flare = {}
    flare = {"name": "flare", "children": [{"name": "wordcloud", "children": [{"name": "adj", "children": wordcloud_a},
                                                                              {"name": "v", "children": wordcloud_v},
                                                                              {"name": "nr", "children": wordcloud_nr},
                                                                              {"name": "n", "children": wordcloud_n}]}]}
    f = open(os.path.join(request.folder,'private','d3','BestComments.json'), 'w+')
    f.write(json.dumps(flare, sort_keys=False, separators=(',', ':'), indent=4))
    f.close()

    f = codecs.open(os.path.join(request.folder,'private','d3','wordcloud.txt'), 'w+', 'utf-8')
    for item in list(set(p_wordclouds)):
        f.write(item + '\n')
    f.close()

    return dict(message="OK")
    #return len(rows)
    #return json.dumps(female_wordclouds_nr)

def ConvertComments():
    rows = fbdb(fbdb.news_comments.comments <> None).select()  #
    for row in rows:
        convertNewsComms(row["fid"])

def delay():
    time.sleep(1.5)
