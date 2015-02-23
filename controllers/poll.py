# coding: utf-8
# try something like
import json
import time
import datetime
import jieba
import jieba.analyse
import string
import re
from collections import Counter
from collections import OrderedDict
import itertools
from snownlp import SnowNLP
from snownlp import sentiment
from datetime import timedelta
import jieba.posseg as pseg
import codecs


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






@auth.requires_login()
def Sex(uid):
    row = fbdb(fbdb.people.uid==uid).select().first()
    if not row:
        user = People(uid)
        gender = user.gender
    else:
        gender = row["gender"] if 'gender' in row else None
    return gender


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
    q_time = now-timedelta(days=56)
    rows = fbdb((fbdb.comments.like_count >= 20)&(fbdb.comments.from_team=='柯文哲')&(fbdb.comments.created_time >=q_time)).select()
    for row in rows:
        #segments = list(set(row['segment']))
        segments = pseg.cut(row['message'])
        count = row["like_count"] // 10
        #count= 1
        wordclouds_a = []
        wordclouds_n = []
        wordclouds_nr = []
        wordclouds_v = []
        for j in range(0, count):
            for i in segments:
                p_wordclouds2.append(i.word)
                if (re.search("^a", i.flag) <> None)&(i.word not in stoplist):
                    wordclouds_a.append(i.word)
                elif (i.flag =='n')&(i.word not in stoplist):
                    wordclouds_n.append(i.word)
                elif (i.flag =='nr')&(i.word not in stoplist):
                    wordclouds_nr.append(i.word)
                elif (re.search("^v", i.flag) <> None)&(i.word not in stoplist):
                    wordclouds_v.append(i.word)
        p_wordclouds.extend(p_wordclouds2)
        userid = row["from_id"]
        user = fbdb(fbdb.people.uid==userid).select().first()
        sex = user['gender']
        #likes = row['likes'] if (('likes' in row) & (row['likes'] != None) & (row['likes'] != {})) else []
        #for like in likes:
        wordcloud_a2.extend(list(set(wordclouds_a)))
        wordcloud_n2.extend(list(set(wordclouds_n)))
        wordcloud_nr2.extend(list(set(wordclouds_nr)))
        wordcloud_v2.extend(list(set(wordclouds_v)))
        
        if sex =='female':
            female_wordclouds.extend(list(set(p_wordclouds2)))
            female_wordclouds_a.extend(list(set(wordclouds_a)))
            female_wordclouds_n.extend(list(set(wordclouds_n)))
            female_wordclouds_nr.extend(list(set(wordclouds_nr)))
            female_wordclouds_v.extend(list(set(wordclouds_v)))
        elif sex =='male':
            male_wordclouds.extend(list(set(p_wordclouds2)))
            male_wordclouds_a.extend(list(set(wordclouds_a)))
            male_wordclouds_n.extend(list(set(wordclouds_n)))
            male_wordclouds_nr.extend(list(set(wordclouds_nr)))
            male_wordclouds_v.extend(list(set(wordclouds_v)))
        else:
            pass
    for item in Counter(wordcloud_a2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_a.append({'name': item[0] , 'size': item[1]})
    for item in Counter(wordcloud_n2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_n.append({'name': item[0] , 'size': item[1]})
    for item in Counter(wordcloud_nr2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_nr.append({'name': item[0] , 'size': item[1]})
    for item in Counter(wordcloud_v2).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        wordcloud_v.append({'name': item[0] , 'size': item[1]})
    
    for item in Counter(female_wordclouds).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud.append({'name': item[0] , 'size': item[1]})
    for item in Counter(male_wordclouds).most_common(150):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud.append({'name': item[0] , 'size': item[1]})

    list_a_female100=[]
    list_n_female100=[]
    list_nr_female100=[]
    list_v_female100=[]
    
    for item in Counter(female_wordclouds_a).most_common(100) :
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_a.append({'name': item[0] , 'size': item[1]})
        list_a_female100.append(item[0])
    
    for item in Counter(female_wordclouds_n).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_n.append({'name': item[0] , 'size': item[1]})
        list_n_female100.append(item[0])
        
    for item in Counter(female_wordclouds_nr).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_nr.append({'name': item[0] , 'size': item[1]})
        list_nr_female100.append(item[0])
        
    for item in Counter(female_wordclouds_v).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        female_wordcloud_v.append({'name': item[0] , 'size': item[1]})
        list_v_female100.append(item[0])
    
    list_a_male100=[]
    list_n_male100=[]
    list_nr_male100=[]
    list_v_male100=[]
    
    for item in Counter(male_wordclouds_a).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_a.append({'name': item[0] , 'size': item[1]})
        list_a_male100.append(item[0])
    
    for item in Counter(male_wordclouds_n).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_n.append({'name': item[0] , 'size': item[1]})
        list_n_male100.append(item[0])
        
    for item in Counter(male_wordclouds_nr).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_nr.append({'name': item[0] , 'size': item[1]})
        list_nr_male100.append(item[0])
    
    for item in Counter(male_wordclouds_v).most_common(100):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        male_wordcloud_v.append({'name': item[0] , 'size': item[1]})
        list_v_male100.append(item[0])
        
    female_wordcloud_a_special =[]
    female_wordcloud_n_special =[]
    female_wordcloud_nr_special =[]
    female_wordcloud_v_special =[]
    
    for item in Counter(female_wordclouds_a).most_common(100):
        if item[0] not in list_a_male100:
            female_wordcloud_a_special.append({'name': item[0] , 'size': item[1]})
    
    for item in Counter(female_wordclouds_n).most_common(100):
        if item[0] not in list_n_male100:
            female_wordcloud_n_special.append({'name': item[0] , 'size': item[1]})

    for item in Counter(female_wordclouds_nr).most_common(100):
        if item[0] not in list_nr_male100:
            female_wordcloud_nr_special.append({'name': item[0] , 'size': item[1]})
        
    for item in Counter(female_wordclouds_v).most_common(100):
        if item[0] not in list_v_male100:
            female_wordcloud_v_special.append({'name': item[0] , 'size': item[1]})
            
    male_wordcloud_a_special =[]
    male_wordcloud_n_special =[]
    male_wordcloud_nr_special =[] 
    male_wordcloud_v_special =[] 
    
    for item in Counter(male_wordclouds_a).most_common(100):
        if item[0] not in list_a_female100:
            male_wordcloud_a_special.append({'name': item[0] , 'size': item[1]})
    
    for item in Counter(male_wordclouds_n).most_common(100):
        if item[0] not in list_n_female100:
            male_wordcloud_n_special.append({'name': item[0] , 'size': item[1]})

    for item in Counter(male_wordclouds_nr).most_common(100):
        if item[0] not in list_nr_female100:
            male_wordcloud_nr_special.append({'name': item[0] , 'size': item[1]})
    
    for item in Counter(male_wordclouds_v).most_common(100):
        if item[0] not in list_v_female100:
            male_wordcloud_v_special.append({'name': item[0] , 'size': item[1]})    
    
            
    flare = {}
    flare = {"name":"flare", "children" : [{"name" : "female_wordcloud", "children":[{"name":"adj", "children":female_wordcloud_a_special},{"name":"v", "children":female_wordcloud_v_special}, {"name":"nr", "children":female_wordcloud_nr_special},{"name":"n", "children":female_wordcloud_n_special}]}] }
    f = open(os.path.join(request.folder,'private','d3','BestComments_female.json'), 'w+')
    f.write(json.dumps(flare,sort_keys=False,separators=(',',':'),indent=4))
    f.close()
    flare = {}
    flare = {"name":"flare", "children" : [{"name" : "male_wordcloud", "children":[{"name":"adj", "children":male_wordcloud_a_special}, {"name":"v", "children":male_wordcloud_v_special}, {"name":"nr", "children":male_wordcloud_nr_special},{"name":"n", "children":male_wordcloud_n_special}]}] }
    f = open(os.path.join(request.folder,'private','d3','BestComments_male.json'), 'w+')
    f.write(json.dumps(flare,sort_keys=False,separators=(',',':'),indent=4))
    f.close()

    flare = {}
    flare = {"name":"flare", "children" : [{"name" : "wordcloud", "children":[{"name":"adj", "children":wordcloud_a},{"name":"v", "children":wordcloud_v}, {"name":"nr", "children":wordcloud_nr},{"name":"n", "children":wordcloud_n}]}] }
    f = open(os.path.join(request.folder,'private','d3','BestComments.json'), 'w+')
    f.write(json.dumps(flare,sort_keys=False,separators=(',',':'),indent=4))
    f.close()
    
    
    f = codecs.open(os.path.join(request.folder,'private','d3','wordcloud.txt'), 'w+', 'utf-8')
    for item in p_wordclouds:
        f.write(item+'\n')
    f.close()
    
    return dict(message="OK")
    #return len(rows)
    #return json.dumps(female_wordclouds_nr)

def HottestComments():
    '''
    import jieba.posseg as pseg
    stoplist = list(delZhStr)
    stoplist.extend(stopwords)
    p_wordclouds = []
    p_wordcloud = []
    rows = fbdb((fbdb.comments.comment_count> 10)&(fbdb.comments.from_team=='柯文哲')).select()
    for row in rows:
        segments = pseg.cut(row['message'])
        count = row["like_count"] // 10
        #count= 1
        #p_wordclouds2 = [i.word for i in segments if i.word not in stoplist]
        p_wordclouds2 = [i.word for i in segments if (i.flag =='a')&(i.word not in stoplist)]
        sex = Sex(row["from_id"])
        if sex =='female':
            p_wordclouds.extend(p_wordclouds2)
        likes = row['likes'] if (('likes' in row)&(row['likes'] != None)&(row['likes'] != {})) else []
        for like in likes:
            if Sex(like["id"]) =='female':
                p_wordclouds.extend(p_wordclouds2)


    for item in Counter(p_wordclouds).most_common(300):
        #s = SnowNLP(item[0]) , 'tag': s.tags
        p_wordcloud.append({'name': item[0], 'size': item[1]})
    flare = {}
    flare = {"name":flare, "children" :p_wordcloud }
    f = open('/Applications/web2py.app/Contents/Resources/applications/fsr/static/HottestComments.json', 'w+')
    f.write(json.dumps(flare,sort_keys=False,separators=(',',':'),indent=4))
    f.close()
    '''
    return dict(message="OK")

def index(): return dict(message="hello from poll.py")

def personal_wordcloud():
    rows = fbdb(fbdb.people.id <> '').select()
    for row in rows:
        user_wordcloud(row['uid'])
    return "OK"

def segmentation():
    rows= fbdb(fbdb.comments.id <> '').select()
    for row in rows:
        fid = row['fid']
        message = row['message']
        segment = list(jieba.cut(message))
        fbdb.comments.update_or_insert(fbdb.comments.fid ==fid, segment=segment)
        fbdb.commit()

@auth.requires_login()
def mentions():
    stoplist = list(delZhStr)
    stoplist.extend(stopwords)
    qstring = ''
    str1= '%支持%柯P%'
    str2='%支持%柯p%'
    str3='%支持%柯文哲%'
    str4 = '%遣辭%'
    str5 = '%做事%'
    str6 = '%感動%'
    str7 = '%性格%'
    #qstring= qstring + str1 +str2 + str3 +str4 +str5 +str6 +str7

    #qstring = '%支持%柯p%'
    qstring = '開車'
    rows= fbdb(fbdb.comments.message.like(qstring)).select()

    #rows= fbdb(fbdb.comments.message.like(qstring) |fbdb.comments.message.like(str2)|fbdb.comments.message.like(str3)|fbdb.comments.message.like(str4)|fbdb.comments.message.like(str5)|fbdb.comments.message.like(str6)|fbdb.comments.message.like(str7)).select()
    all_dict = []
    g_dict= []
    b_dict= []
    comments = []
    g_comments=[]
    b_comments=[]
    people = []
    g_people = []
    b_people = []
    all_time = []
    g_time=[]
    b_time = []
    male_time=[]
    female_time = []
    female_comments=[]
    male_comments=[]
    female = []
    male = []

    for row in rows:
        userid = row['from_id']
        comment = row['message']

        created_time = row['created_time'].strftime('%Y-%m-%dT%H:%M:%S')
        people.append(userid)
        comments.append(comment)
        all_time.append(created_time)

        user = fbdb(fbdb.people.uid==userid).select().first()
        if user:
            if user['gender'] == 'male':
                male.append(userid)
                male_comments.append(comment)
                male_time.append(created_time)
            elif user['gender'] == 'female':
                female.append(userid)
                female_comments.append(comment)
                female_time.append(created_time)

        if row['from_team'] == '柯文哲':
            g_people.append(userid)
            g_comments.append(comment)
            g_time.append(created_time)
            #g_dict.update({comment + ' by ' + userid : created_time.strftime('%Y-%m-%dT%H:%M:%S')})
        else:
            b_people.append(userid)
            b_comments.append(comment)
            b_time.append(created_time)
            #b_dict.update({comment + ' by ' + userid : created_time.strftime('%Y-%m-%dT%H:%M:%S')})


    a1 = list(set(zip(people,comments)))
    a2 = dict(itertools.izip(comments, all_time))
    a_orderdict = OrderedDict()
    for a in a1:
        uid = a[0]
        temp = a_orderdict[uid] if uid in a_orderdict else []
        s = SnowNLP(a[1])
        temp.append({"comments" : a[1] , "update_time" : a2[a[1]], "sentiments" : s.sentiments})
        a_orderdict.update({uid : temp})

    g1 = list(set(zip(g_people,g_comments)))
    g2 = dict(itertools.izip(g_comments, g_time))
    g_orderdict = OrderedDict()
    for g in g1:
        uid = g[0]
        temp = g_orderdict[uid] if uid in g_orderdict else []
        s = SnowNLP(g[1])
        temp.append({"comments" : g[1] , "update_time" : g2[g[1]], "sentiments" : s.sentiments})
        g_orderdict.update({uid : temp})

    b1 = list(set(zip(b_people,b_comments)))
    b2 = dict(itertools.izip(b_comments, b_time))
    b_orderdict = OrderedDict()
    for b in b1:
        uid = b[0]
        temp = b_orderdict[uid] if uid in b_orderdict else []
        s = SnowNLP(b[1])
        temp.append({"comments" : b[1] , "update_time" : b2[b[1]], "sentiments" : s.sentiments})
        b_orderdict.update({uid : temp})

    f1 = list(set(zip(female,female_comments)))
    f2 = dict(itertools.izip(female_comments, female_time))
    f_orderdict = OrderedDict()
    for f in f1:
        uid = f[0]
        temp = f_orderdict[uid] if uid in f_orderdict else []
        s = SnowNLP(f[1])
        temp.append({"comments" : f[1] , "update_time" : f2[f[1]], "sentiments" : s.sentiments})
        f_orderdict.update({uid : temp})

    m1 = list(set(zip(male,male_comments)))
    m2 = dict(itertools.izip(male_comments, male_time))
    m_orderdict = OrderedDict()
    for m in m1:
        uid = m[0]
        temp = m_orderdict[uid] if uid in m_orderdict else []
        s = SnowNLP(m[1])
        temp.append({"comments" : m[1] , "update_time" : m2[m[1]], "sentiments" : s.sentiments})
        m_orderdict.update({uid : temp})


    wordclouds = []
    m_arr=[]
    for person in list(set(people)):
        m_arr = a_orderdict[person]
        segments=[]
        for m in m_arr:
            segment=[]
            segment = list(jieba.cut(m['comments']))
            segments.extend(segment)
        segments = list(set(segments))
        wordclouds2 = [i for i in segments if i not in stoplist]
        wordclouds.extend(wordclouds2)
    wordcloud=[]
    for item in Counter(wordclouds).most_common(1000):
        wordcloud.append({'count': item[1] , 'value': item[0]})

    b_wordclouds = []
    b_arr=[]
    for person in list(set(b_people)):
        m_arr = b_orderdict[person]
        segments=[]
        for m in m_arr:
            segment=[]
            segment = list(jieba.cut(m['comments']))
            segments.extend(segment)
        segments = list(set(segments))
        b_wordclouds2 = [i for i in segments if i not in stoplist]
        b_wordclouds.extend(b_wordclouds2)
    b_wordcloud=[]
    for item in Counter(b_wordclouds).most_common(1000):
        b_wordcloud.append({'count': item[1] , 'value': item[0]})

    g_wordclouds = []
    g_arr=[]
    for person in list(set(g_people)):
        m_arr = g_orderdict[person]
        segments=[]
        for m in m_arr:
            segment=[]
            segment = list(jieba.cut(m['comments']))
            segments.extend(segment)
        segments = list(set(segments))
        g_wordclouds2 = [i for i in segments if i not in stoplist]
        g_wordclouds.extend(g_wordclouds2)
    g_wordcloud=[]
    for item in Counter(g_wordclouds).most_common(1000):
        g_wordcloud.append({'count': item[1] , 'value': item[0]})


    male_wordclouds = []
    male_arr=[]
    for person in list(set(male)):
        m_arr = m_orderdict[person]
        segments=[]
        for m in m_arr:
            segment=[]
            segment = list(jieba.cut(m['comments']))
            segments.extend(segment)
        segments = list(set(segments))
        male_wordclouds2 = [i for i in segments if i not in stoplist]
        male_wordclouds.extend(male_wordclouds2)
    male_wordcloud=[]
    for item in Counter(male_wordclouds).most_common(1000):
        male_wordcloud.append({'count': item[1] , 'value': item[0]})


    female_wordclouds = []
    female_arr=[]
    for person in list(set(female)):
        m_arr = f_orderdict[person]
        segments=[]
        for m in m_arr:
            segment=[]
            segment = list(jieba.cut(m['comments']))
            segments.extend(segment)
        segments = list(set(segments))
        female_wordclouds2 = [i for i in segments if i not in stoplist]
        female_wordclouds.extend(female_wordclouds2)
    female_wordcloud=[]
    for item in Counter(female_wordclouds).most_common(1000):
        female_wordcloud.append({'count': item[1] , 'value': item[0]})


    a_list= []
    a_list= list(set(people))
    male = 0
    female = 0
    for person in a_list:
        row = fbdb(fbdb.people.uid == person).select().first()
        if row:
            gender = row['gender']
            if gender == 'male':
                male+= 1
            elif gender == 'female':
                female += 1
            else:
                pass
    b_list=[]
    b_list= list(set(b_people))
    b_male = 0
    b_female = 0
    for person in b_list:
        row = fbdb(fbdb.people.uid == person).select().first()
        if row:
            gender = row['gender']
            if gender == 'male':
                b_male+= 1
            elif gender == 'female':
                b_female += 1
            else:
                pass
    g_list=[]
    g_list= list(set(g_people))
    g_male = 0
    g_female = 0

    for person in g_list:
        row = fbdb(fbdb.people.uid == person).select().first()
        if row:
            gender = row['gender']
            if gender == 'male':
                g_male+= 1
            elif gender == 'female':
                g_female += 1
            else:
                pass

    stat = {"All":{"total": len(set(people)), "male": male, "female": female} , "Blue": {"total": len(set(b_people)), "male": b_male, "female": b_female} , "Green":  {"total": len(set(g_people)), "male": g_male, "female": g_female} }

    comment_arr=json.dumps(a_orderdict, sort_keys=False,separators=(',',':'),indent=4)
    b_comment_arr=json.dumps(b_orderdict, sort_keys=False,separators=(',',':'),indent=4)
    g_comment_arr=json.dumps(g_orderdict, sort_keys=False,separators=(',',':'),indent=4)
    female_comment_arr=json.dumps(f_orderdict, sort_keys=False,separators=(',',':'),indent=4)
    male_comment_arr=json.dumps(m_orderdict, sort_keys=False,separators=(',',':'),indent=4)

    fbdb.mentions.insert(qstring=qstring, comment_arr = comment_arr, b_comment_arr = b_comment_arr,  g_comment_arr = g_comment_arr, male_comment_arr=male_comment_arr, female_comment_arr=female_comment_arr, comment_count = len(set(comments)), b_comment_count = len(set(b_comments)), g_comment_count = len(set(g_comments)), user_count = len(set(people)), b_user_count = len(set(b_people)), g_user_count = len(set(g_people)), updated_time=datetime.datetime.now(), stat=stat, wordcloud=wordcloud, female_wordcloud=female_wordcloud, male_wordcloud=male_wordcloud, b_wordcloud=b_wordcloud, g_wordcloud=g_wordcloud )

    user_arr = json.dumps(a_orderdict, sort_keys=False,separators=(',',':'),indent=4)
    with open('/usr/local/lib/python2.7/site-packages/snownlp/sentiment/blue.txt','a') as file:
        for item in g_comments:
            print>>file, item
    return "OK"

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
