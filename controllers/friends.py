# coding: utf8
# try something like
import datetime
import time
from collections import Counter
import urllib2
import json




def index(): return dict(message="hello from friends.py")



def test():
    post=getFriends('509822796') 
    return str(post)

@auth.requires_login()
def findFriends():
    graph = getGraph()
    posts_data=graph.request("me/friends", args={'fields':'id', 'limit':2000})
    time.sleep(1.3)
    posts= posts_data['data']
    for post in posts:
        getFriends(post["id"])
        time.sleep(1.3)

@auth.requires_login()        
def taipeiFriend():
    rows = fbdb(fbdb.friends.locale <> "zh_TW").select()
    graph = getGraph()
    for row in rows:  
        userid = row["uid"]
        
        #hometown = row['hometown']["name"] if row['hometown'] != None else None
        #if hometown == 'Taipei, Taiwan':
        #    try:
        #        posts_data=graph.request(userid, args={'fields':'likes.limit(2000),id'})
        #        time.sleep(1.3)
        #    except:
        #        raise
        #        posts_data = {}
        #    likes = posts_data["likes"]["data"] if "likes" in posts_data else []
        #if row["likes"] == []:
        try:
            posts_data=graph.request(userid, args={'fields':'likes.limit(2000),id'})
            time.sleep(1.3)
            likes = posts_data["likes"]["data"] if "likes" in posts_data else []
            fbdb.friends.update_or_insert(fbdb.friends.uid==userid, likes=likes)
            fbdb.commit()
        except:
            raise
            #pass
    return "OK"
            
@auth.requires_login()
def getFriends(userid):
    try:
        graph = getGraph()
        posts_data=graph.request(userid, args={'fields':'id,first_name,last_name,locale,gender,link,location,name,updated_time,birthday,age_range,hometown,education,timezone,work,picture, relationship_status'})
        post = {}
        post = posts_data
    except GraphAPIError, e:
        #raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=userid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
        return "Not a person id"
    try:
        uid = post["id"]
        first_name =  post["first_name"] if ('first_name' in post) else ''
        last_name = post["last_name"] if ('last_name' in post) else ''
        locale  = post["locale"] if ('locale' in post) else ''
        gender  = post["gender"] if ('gender' in post) else ''
        religion  = post["religion"] if ('religion' in post) else ''
        location  = post["location"] if ('location' in post) else ''
        name  = post["name"] if ('name' in post) else ''
        website  = post["website"] if ('website' in post) else ''
        relationship_status   =  post["relationship_status"] if ('relationship_status' in post) else ''
        updated_time = datetime.datetime.strptime(post["updated_time"],'%Y-%m-%dT%H:%M:%S+0000') if ('updated_time' in post) else ''
        age_range  = post["age_range"] if ('age_range' in post) else ''
        birthday  = post["birthday"] if ('birthday' in post) else ''
        hometown  = post["hometown"] if ('hometown' in post) else ''
        education  = post["education"] if ('education' in post) else ''
        timezone  = post["timezone"] if ('timezone' in post) else ''
        work  = post["work"] if ('work' in post) else ''
        email  = post["email"] if ('email' in post) else ''
        link = post["link"] if ('link' in post) else ''
        picture = post["picture"]["data"]["url"] if ('picture' in post) else ''
        row = fbdb(fbdb.friends.uid==uid).select().first()
        if row:
            row.update_record(first_name=first_name, last_name=last_name, locale=locale, gender=gender, religion=religion, location=location, name=name, website=website, relationship_status=relationship_status, updated_time=updated_time, age_range=age_range, hometown=hometown, education=education, timezone=timezone, work=work, email=email, link=link, picture=picture, birthday=birthday)
        else:
            fbdb.friends.insert(uid=uid, first_name=first_name, last_name=last_name, locale=locale, gender=gender, religion=religion, location=location, name=name, website=website, relationship_status=relationship_status, updated_time=updated_time, age_range=age_range, hometown=hometown, education=education, timezone=timezone, work=work, email=email, link=link, picture=picture, birthday=birthday)
            fbdb.commit()
        message = "all posts finished"
    except GraphAPIError, e:
        #raise
        message=e.result
        fbdb.graphAPI_Error.insert(oid=uid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()


    return post

#@auth.requires_login()
def Top_likes_politician():
    #rows = fbdb(fbdb.comments.fid == '497419873693331_497440607024591').select()
    rows = fbdb(fbdb.friends.id <> '').select()
    top_like = []
    likes=[]
    top_likes=[]

    for row in rows:
        likes= row['likes']
        likes_array=[]
        for like in likes:
            if like["category"].lower() == 'politician':
                likes_array.append(like["id"])

                
        top_like.extend(likes_array)

    for item in Counter(top_like).most_common(1000):
        top_likes.append({'count': item[1] , 'value': item[0]})
        getPolitician(item[0])
        time.sleep(1.3)        
    

    fbdb.top_likes.insert(top_likes=top_likes, updated_time = datetime.datetime.now())
    fbdb.commit()
    return "OK"


@auth.requires_login()
def getPolitician(gid):
    graph = getGraph()
    try:
        if gid:
            fb_obj = graph.get_object(gid)
            id= fb_obj["id"]
            row = fbdb.politician(fid=id)
            if not row:
                fid = fb_obj["id"]
                name =  fb_obj["name"] if ('name' in fb_obj) else ''
                category = fb_obj["category"] if ('category' in fb_obj) else ''
                about = fb_obj["about"] if ('about' in fb_obj) else ''
                can_post = fb_obj["can_post"] if ('can_post' in fb_obj) else ''
                is_published = fb_obj["is_published"] if ('is_published' in fb_obj) else ''
                talking_about_count = fb_obj["talking_about_count"] if ('talking_about_count' in fb_obj) else ''
                were_here_count = fb_obj["were_here_count"] if ('were_here_count' in fb_obj) else ''
                link = fb_obj["link"] if ('link' in fb_obj) else ''
                likes = fb_obj["likes"] if ('likes' in fb_obj) else ''
                description = fb_obj["description"] if ('description' in fb_obj) else ''
                updated_time = fb_obj["updated_time"] if ('updated_time' in fb_obj) else ''
                cover_id = fb_obj["cover"]["cover_id"] if ('cover' in fb_obj) else ''
                cover_source = fb_obj["cover"]["source"] if ('cover' in fb_obj) else ''
                locale = fb_obj["locale"] if ('locale' in fb_obj) else ''
                website = fb_obj["website"] if ('website' in fb_obj) else ''
                fbdb.politician.insert(fid=fid, name=name, category=category, about=about, can_post=can_post, is_published=is_published, link=link, description=description,  updated_time=updated_time, cover_id=cover_id, cover_source=cover_source,locale=locale,website=website)
            fbdb.commit()
            message='Successfully adding new page into the database'
        else:
            message='failure, please check your pageid!'
    except GraphAPIError, e:
        raise
        message=e.result
        fbdb.graphAPI_Error.insert(placeid=gid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    except:
        raise
        message=  "Unexpected error:", sys.exc_info()[0]
        fbdb.graphAPI_Error.insert(placeid=gid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    return dict(message=message)


def check_party(name):
    #name = '周守訓'
    response = urllib2.urlopen('http://zh.wikipedia.org/w/api.php?format=json&action=query&titles=' + name + '&prop=revisions&rvprop=content&format=json&rvsection=0')
    r_json = {}
    r_json = json.loads(response.read())
    party = json.dumps(r_json["query"]["pages"], ensure_ascii=False)
    st = party.find(r"party =")
    party = party[st:]
    party=party.split(r'|educate')[0][8:].rstrip(r'\n').upper()
    party_list=[]
    if 'KMT' in party:
        party_list.append("KMT")
    if 'DPP' in party:
        party_list.append("DPP")
    if 'TSU' in party:
        party_list.append("TSU")
    if 'NPSU' in party:
        party_list.append("NPSU")
    if 'PFP' in party:
        party_list.append("PFP")        
    if 'NP' in party:
        party_list.append("NP")        
    if 'GPTW' in party:
        party_list.append("GPTW")        
    if '無黨籍' in party:
        party_list.append("NONEP")  
    return party_list
    
def renew_politician():
    rows = fbdb(fbdb.politician.id <> '').select()
    for row in rows:
        party=[]
        party = check_party(row["name"])
        time.sleep(1.0)
        row.update_record(party={"result":party})
    return "OK"


def check_alluser_color():
    rows = fbdb(fbdb.friends.uid <>"").select()
    blue = 0
    green = 0 
    blue_count = 0
    green_count = 0
    Neu_count = 0
    
    for row in rows:
        userid = row["uid"]
        color = check_user_color(userid)
        if color != None:
            if color > 0 :
                blue += color
                blue_count +=1
            if color < 0 :
                green += color
                green_count +=1
            if color == 0 :
                Neu_count += 1
        row.update_record(color=color)
    result = {"score": {"blue": blue, "green": green}, "count":{"blue": blue_count, "green": green_count, "others": Neu_count}}
    fbdb.pcolor.insert(result=result)
    return "OK"

def check_user_color(userid):
    #userid='100000271152766'
    row = fbdb(fbdb.friends.uid == userid).select().first()
    likes= row['likes']
    color = 0
    check = False
    for like in likes:
        if like["category"].lower() == 'politician':
            cid = like["id"]
            p_color = politician_party(cid)
            if p_color != None:
                check = True
                color += p_color
    if check == True:
        return color
    else:
        return None
            
def politician_party(cid):
    #cid="195170935780"
    row = fbdb(fbdb.politician.fid == cid).select().first()
    party_list = row["party"]["result"]
    color = 0
    try:
        party = party_list[len(party_list)-1]
        if 'KMT' in party:
            color = 2
        if 'DPP' in party:
            color = -2
        if 'TSU' in party:
            color = -3
        if 'NPSU' in party:
            color = 0
        if 'PFP' in party:
            color = 1
        if 'NP' in party:
            color = 3
        if 'GPTW' in party:
            color = 0  
        if 'NONEP' in party:
            color = 0
        return color
    except:

        return None

@auth.requires_login()    
def fb_news():
    import urllib
    graph = getGraph()
    post_data = graph.fql("select title, url, owner, created_time from link where owner in (select uid2 from friend where uid1 = me() limit 10) and created_time > 1406400000 ORDER BY created_time DESC")
    time.sleep(1.3)
    post = []
    post = post_data["data"]
    fbdb.pcolor.insert(result=post_data)
    fbdb.commit()
    urls="url = '" + post[0]["url"].encode('utf-8') + "'"
    start = 1
    end = len(post)
    r_jsons=[]
    links=[]
    for i in range(start, end):
        link = post[i]
        url="url = '" + link["url"].encode('utf-8') + "'"
        if i % 10 == 0:
            link_data = graph.fql("SELECT url, normalized_url, share_count, like_count, comment_count, total_count, commentsbox_count, comments_fbid, click_count FROM link_stat WHERE " + urls)
            links = link_data["data"]
            time.sleep(2)
            r_jsons.extend(links)
            urls=url
        else:
            urls += " or " + url
    link_data = graph.fql("SELECT url, normalized_url, share_count, like_count, comment_count, total_count, commentsbox_count, comments_fbid, click_count FROM link_stat WHERE " + urls)
    links = link_data["data"]
    #time.sleep(2)
    r_jsons.extend(links)
    rank = []
    for url in r_jsons:
        score = url["like_count"] * 0.2 + url["share_count"] * 0.5 + url["comment_count"] * 0.3
        rank.append((score, url["normalized_url"]))
    ranks=sorted(rank, key = lambda x : x[0],reverse=True)
    fbdb.pcolor.insert(result=ranks)
    fbdb.commit()
    return len(post)
