# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################

from facebook import GraphAPI, GraphAPIError
from geojson import Feature, Point, FeatureCollection
import geojson
import json



#@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simple replace the two lines below with:
    return auth.wiki()

    """
    
    
    user = auth.user
    if user:
        
        response.flash = T('You are %(name)s', dict(name=user['first_name']))
        return dict(message=T('Hello, Facebook is telling that you are %(first_name)s %(last_name)s', dict(first_name=user['first_name'], last_name=user['last_name'])))
    response.flash = T('Welcome to web2py')
    return dict(message=T('Hello, please login'))

#@auth.requires_login()

@auth.requires_login()
def display_form():
    allplaces = SQLFORM.grid(fbdb.place,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allplaces=allplaces)

def display_page():
    allpages = SQLFORM.grid(fbdb.page,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allpages=allpages)

def display_poi():
    allpois = SQLFORM.grid(fbdb.place,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allpois=allpois)

def display_news():
    allnews = SQLFORM.grid(fbdb.news,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allnews=allnews)


def display_people():
    allpeople = SQLFORM.grid(fbdb.people,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allpeople=allpeople)

def display_post():
    #allposts = SQLFORM.grid(fbdb.post,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')
    allposts= fbdb().select(fbdb.post.ALL)
    return dict(allposts=allposts)

def display_event():
    allevents = SQLFORM.grid(fbdb.event,user_signature=False, create=False, deletable=True, editable=False,paginate=10, maxtextlength = 100, orderby = 'id DESC')

    return dict(allevents=allevents)


@auth.requires_login()
def addplace():
    form = FORM('Facebook place id or Name',
              INPUT(_name='fid', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        placeid= request.vars['placeid']
        message = getPage(fid)
        response.flash = str(message) #'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@auth.requires_login()
def addPage():
    form = FORM('Facebook page id or Name',
              INPUT(_name='fid', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        gid= request.vars['fid']
        message = getPage(gid)
        response.flash = str(message) #'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@auth.requires_login()
def addpeople():
    form = FORM('Facebook user id or Name',
              INPUT(_name='uid', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        gid= request.vars['uid']
        message = getPeople(gid)
        response.flash = str(message) #'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@auth.requires_login()
def addpost():
    form = FORM('Facebook post id',
              INPUT(_name='uid', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        gid= request.vars['uid']
        message = getPost(gid)
        response.flash = str(message) #'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@auth.requires_login()
def addevent():
    form = FORM('Facebook event id',
              INPUT(_name='uid', requires=IS_NOT_EMPTY()),
              INPUT(_type='submit'))
    if form.accepts(request,session):
        gid= request.vars['uid']
        message = getEvent(gid)
        response.flash = str(message) #'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form)

@auth.requires_login()
def getP(gid):
    graph = getGraph()
    try:
        if gid:
            fb_obj = graph.get_object(gid)
            id= fb_obj["id"]
            row = fbdb.place(placeid=id)
            if not row:
                name =  fb_obj["name"] if 'name' in fb_obj else ""
                category = fb_obj["category"] if 'category' in fb_obj else ""
                category_list =  fb_obj["category_list"] if 'category_list' in fb_obj else ""
                checkins= fb_obj["checkins"] if 'checkins' in fb_obj else ""
                if 'location' in fb_obj:
                    zipcode= fb_obj["location"]["zip"] if ("zip" in fb_obj["location"]) else ""
                    latitude= fb_obj["location"]["latitude"] if ("latitude" in fb_obj["location"]) else ""
                    longitude= fb_obj["location"]["longitude"] if ("longitude" in fb_obj["location"])  else ""
                link= fb_obj["link"]
                old_ids = ''
                fbdb.place.insert(placeid=id,name = name,latitude=latitude,longitude=longitude,category=category,category_list=category_list,zipcode=zipcode,link=link,old_ids=old_ids)

            fbdb.commit()
            message='Successfully adding new place into the database'
        else:
            message='failure, please check your placeid!'
    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(placeid=gid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit()
    except :
        raise
        message = "unknown error"

    return dict(message=message)





@auth.requires_login()
def getEvent(eid):
    graph = getGraph()
    event= graph.get_object(eid)
    eventid = event["id"] if 'id' in event else ''
    row = fbdb.event(eventid=eventid)
    try:
        if not row:
            description = event["description"] if 'description' in event else ''
            end_time  = event["end_time"] if 'end_time' in event else ''
            timezone = event["timezone"] if 'timezone' in event else ''
            name = event["name"] if 'name' in event else ''
            location = event["location"] if 'location' in event else ''
            ownerid = event["owner"]["id"] if 'owner' in event else ''
            ownername = event["owner"]["name"] if 'owner' in event else ''
            picture = event["picture"] if 'picture' in event else ''
            privacy = event["privacy"] if 'privacy' in event else ''
            start_time = event["start_time"] if 'start_time' in event else ''
            ticket_uri = event["ticket_uri"] if 'ticket_uri' in event else ''
            updated_time = event["updated_time"] if 'updated_time' in event else ''
            is_date_only  = event["is_date_only"] if 'is_date_only' in event else ''
            if 'venue' in event:
                venueid  = event["venue"]["id"] if 'id' in event["venue"] else ''
                venuename = event["venue"]["name"] if 'name' in event["venue"] else ''
                country = event["venue"]["country"] if 'country' in event["venue"] else ''
                city = event["venue"]["city"] if 'city' in event["venue"] else ''
                state  = event["venue"]["state"] if 'state' in event["venue"] else ''
                street = event["venue"]["street"] if 'street' in event["venue"] else ''
                zipcode = event["venue"]["zip"] if 'zip' in event["venue"] else ''
                longitude = event["venue"]["longitude"] if 'longitude' in event["venue"] else ''
                latitude  = event["venue"]["latitude"] if 'latitude' in event["venue"] else ''
            fbdb.event.update_or_insert(eventid==eventid, eventid=eventid,description=description, end_time=end_time, timezone=timezone, name=name, location=location, ownerid=ownerid, ownername= ownername, picture=picture, privacy=privacy, start_time=start_time, ticket_uri=ticket_uri, updated_time=updated_time, is_date_only=is_date_only, venuename=venuename, venueid=venueid, country=country, city=city, state=state, street=street, zipcode=zipcode, longitude=longitude, latitude=latitude)
            fbdb.commit()
            message='Successfully adding new event into the database'    
        else:
            message='Already have this event!!!'       
    except GraphAPIError, e:
        message=e.result
        fbdb.graphAPI_Error.insert(placeid=gid,date_time=datetime.datetime.today(),error_msg=message)
        fbdb.commit() 
    
    
    return dict(message=message) 

@auth.requires_login()
def social_counts_pages():
    from datetime import datetime ,date
    from time import strptime
    from dateutil.relativedelta import relativedelta

    pageid = request.args(0)  or redirect(URL('index'))
    pagename = fbdb(fbdb.page.pageid== pageid).select()[0].name

    #social_counts = fbdb(fbdb.social_counts.placeid== placeid).select()
    query = fbdb.social_counts.placeid == pageid
    #social_counts = SQLFORM.smartgrid(fbdb.social_counts,constraints = {'social_counts':query},user_signature=False, create=False, deletable=False, editable=False, maxtextlength = 240)
    social_counts = SQLFORM.grid(query,fbdb.social_counts,user_signature=False, create=False, deletable=False, editable=False,paginate=240, maxtextlength = 240, orderby = 'id DESC')
    first_rec = fbdb(fbdb.social_counts.placeid== pageid).select(fbdb.social_counts.ALL).first().date_time
    year = first_rec.year
    month = first_rec.month
    dt = datetime.now()
    year2 = dt.year
    month2 = dt.month
    dtlist = []
    while (year <= year2) :
        if (year == year2):
            if (month <= month2):
                m_str = '0' + str(month) if month < 10 else str(month)
                dtlist.append(str(year) + '-' + str(m_str))
        else:
            dtlist.append(str(year) + '-' + str(month))
        first_rec = first_rec + relativedelta(months = 1)
        year = first_rec.year
        month = first_rec.month
    return dict(social_counts=social_counts, pagename=pagename,dtlist=dtlist,pageid=pageid)

@auth.requires_login()
def social_counts():
    from datetime import datetime ,date
    from time import strptime
    from dateutil.relativedelta import relativedelta

    placeid = request.args(0)  or redirect(URL('index'))
    placename = fbdb(fbdb.place.placeid== placeid).select()[0].name

    #social_counts = fbdb(fbdb.social_counts.placeid== placeid).select()
    query = fbdb.social_counts.placeid == placeid
    #social_counts = SQLFORM.smartgrid(fbdb.social_counts,constraints = {'social_counts':query},user_signature=False, create=False, deletable=False, editable=False, maxtextlength = 240)
    social_counts = SQLFORM.grid(query,fbdb.social_counts,user_signature=False, create=False, deletable=False, editable=False,paginate=240, maxtextlength = 240, orderby = 'id DESC')
    first_rec = fbdb(fbdb.social_counts.placeid== placeid).select(fbdb.social_counts.ALL).first().date_time
    year = first_rec.year
    month = first_rec.month
    dt = datetime.now()
    year2 = dt.year
    month2 = dt.month
    dtlist = []
    while (year <= year2) :
        if (year == year2):
            if (month <= month2):
                m_str = '0' + str(month) if month < 10 else str(month)
                dtlist.append(str(year) + '-' + str(m_str))
        else:
            dtlist.append(str(year) + '-' + str(month))
        first_rec = first_rec + relativedelta(months = 1)
        year = first_rec.year
        month = first_rec.month
    latitude =  fbdb(fbdb.place.placeid== placeid).select().first().latitude
    longitude =  fbdb(fbdb.place.placeid== placeid).select().first().longitude
    return dict(social_counts=social_counts, placename=placename,latitude=latitude,longitude=longitude,dtlist=dtlist,placeid=placeid)

@auth.requires_login()
def social_counts_month():
    from datetime import datetime ,date
    pageid = request.args(0) or redirect(URL('index'))
    pagename = fbdb(fbdb.page.pageid== pageid).select()[0].name
    year = request.args(1).split('-')[0]
    month = request.args(1).split('-')[1]
    from_date = datetime.strptime(str(year) + '-'+ str(month) +'-01 00:00:00','%Y-%m-%d %H:%M:%S')
    month2 = int(month) +1 if int(month) < 12 else 1
    year2 = int(year) if int(month) < 12 else int(year)+1
    to_date = datetime.strptime(str(year2) + '-'+ str(month2) +'-01 00:00:00','%Y-%m-%d %H:%M:%S')
    pagename = fbdb(fbdb.page.pageid== pageid).select()[0].name
    #rec = fbdb.social_counts.placeid == placeid
    #rec1= fbdb.social_counts.date_time >= from_date
    #rec2= fbdb.social_counts.date_time < to_date
    #constraints = {'social_counts':rec & rec1 & rec2}
    rows = fbdb((fbdb.social_counts.placeid == pageid) & (fbdb.social_counts.date_time >= from_date) & (fbdb.social_counts.date_time < to_date)).select()
    #social_counts = SQLFORM.smartgrid(fbdb.social_counts,constraints = constraints,args=[request.args(0),request.args(1)],user_signature=False, create=False, deletable=False, editable=False,paginate=240, maxtextlength = 240, orderby = 'id DESC')
    return dict(pagename=pagename,date = request.args(1),rows=rows)

@auth.requires_login()
def social_countsall_month():
    from datetime import datetime ,date
    year = request.args(0).split('-')[0]
    month = request.args(0).split('-')[1]
    from_date = datetime.strptime(str(year) + '-'+ str(month) +'-01 00:00:00','%Y-%m-%d %H:%M:%S')
    month2 = int(month) +1 if int(month) < 12 else 1
    year2 = int(year) if int(month) < 12 else int(year)+1
    to_date = datetime.strptime(str(year2) + '-'+ str(month2) +'-01 00:00:00','%Y-%m-%d %H:%M:%S')
    rows = fbdb((fbdb.social_counts.date_time >= from_date) & (fbdb.social_counts.date_time < to_date)).select()
    #query = ( fbdb.social_counts.date_time >= from_date) & (fbdb.social_counts.date_time < to_date)
    #social_counts = SQLFORM.grid(query,fbdb.social_counts,user_signature=False, create=False, deletable=False, editable=False,paginate=240, maxtextlength = 240, orderby = 'id DESC')
    return dict(date=request.args(0),rows=rows)

@auth.requires_login()
def social_counts_all():
    from datetime import datetime ,date
    from time import strptime
    from dateutil.relativedelta import relativedelta
    first_rec = fbdb().select(fbdb.social_counts.ALL,limitby=(0, 2)).first().date_time
    year = first_rec.year
    month = first_rec.month
    dt = datetime.now()
    year2 = dt.year
    month2 = dt.month
    dtlist = []
    while (year <= year2) :
        if (year == year2):
            if (month <= month2):
                m_str = '0' + str(month) if month < 10 else str(month)
                dtlist.append(str(year) + '-' + str(m_str))
        else:
            dtlist.append(str(year) + '-' + str(month))
        first_rec = first_rec + relativedelta(months = 1)
        year = first_rec.year
        month = first_rec.month
    social_counts = SQLFORM.grid(fbdb.social_counts,user_signature=False, create=False, deletable=False, editable=False,paginate=100, maxtextlength = 240, orderby = 'id DESC')
    return dict(social_counts=social_counts,dtlist=dtlist)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
