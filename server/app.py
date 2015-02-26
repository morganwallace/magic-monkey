#!/usr/bin/env python
# -*- coding: utf8 -*-

from subprocess import check_output
import flask
import operator
from flask import request, url_for, abort, jsonify, Flask, Response, make_response
from os import environ
from flaskext.bcrypt import Bcrypt
# from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.gzip import Gzip
from flask.ext.compress import Compress
import MySQLdb
import datetime
import json
from lxml import html
from urllib import urlopen

app = flask.Flask(__name__)
Compress(app)
bcrypt = Bcrypt(app)
# gzip = Gzip(app)

app.debug = True
db=MySQLdb.connect(host="sql3.freemysqlhosting.net",user="sql368787",
                  passwd="aY1!uB9!",db="sql368787",port=3306)
cursor = db.cursor()


###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET','POST'])
def home():
    
    """Builds a template based on a GET request, with some default
    arguements"""  
    if request.method == 'GET':
        
        if 'userId' in request.cookies:
            if request.cookies['userId'] != "":
                userLinks = dbLinksToDict(request.cookies['userId']) 
                username = str(getUsername(request.cookies['userId']))
                return flask.render_template(
                    'home.html',
                    username=username,
                    links=userLinks) 

        return flask.render_template(
            'home.html',
            username="",
            links=[])

### 
# Signup Resource:
# use AJAX, should return json or write values in the http response
# set userId in cookie once user record created if username not unique return false
###

@app.route('/signup', methods=['POST'])
def signup():
     app.logger.debug("signup button clicked")
         
     username = str(MySQLdb.escape_string(request.form['username']))
     password = str(MySQLdb.escape_string(request.form['password']))

     #check if username exists
     app.logger.debug(userNameExists(username))
     if not userNameExists(username):
         #create new row in table USERS 
         pw_hash = bcrypt.generate_password_hash(password)     
         addNewUserToDB(username, pw_hash, 1)
         app.logger.debug("Signup successful")
         
         userId = getUserId(username)
         #set cookie to indicate user logged in     
         resp = make_response(jsonify(success=True, username=username))
         #app.logger.debug(userId)
         resp.set_cookie('userId', str(userId)) 
         return resp
     else:
         app.logger.debug("Username already exists")
         resp = make_response(jsonify(success=False, reason="Username already exists, choose another username"))
         return resp


### 
# Login Resource:
# use AJAX, should return json or write values in the http response
# 
###

@app.route('/login', methods=['POST'])
def login():
     username = str(MySQLdb.escape_string(request.form['username']))
     password = str(MySQLdb.escape_string(request.form['password']))

     app.logger.debug("login button clicked")
     #check for existing user record in table USERS 
     
     cursor.execute("""SELECT * FROM USERS WHERE USER_NAME = %s""", username )
     app.logger.debug(cursor._executed)
     db.commit()

     row = cursor.fetchone()
     app.logger.debug(row) 
     if row:
         pw_hash = row[2]
         #check if password matches
         if bcrypt.check_password_hash(pw_hash, password): 
             app.logger.debug("password found")
             setLoginStatus(str(row[0]), 1)
             jsonResponse = {}
             jsonResponse['links'] =  dbLinksToDict(str(row[0]))
             jsonResponse['success'] = True
             jsonResponse['username'] = str(row[1])            
             resp = Response(json.dumps(jsonResponse), mimetype='application/json')
             #resp = jsonify(success=True, username=username, links=jsonLinks))
             resp.set_cookie('userId', str(row[0]))
             return resp
         else:
             app.logger.debug("password not found")
             return make_response(jsonify(success=False, reason="Password does not match our records"))
     else:
         app.logger.debug("username not found in database")
         return make_response(jsonify(success=False, reason="Username does not match our records"))

####
# Logout
#
###

@app.route('/logout', methods=['POST'])
def logout():  
   if 'userId' in request.cookies:  
        setLoginStatus(request.cookies['userId'], 0)
        resp = make_response(jsonify(success=True, type='logout'))
        resp.set_cookie('userId', '')
        return resp
   else:
        resp = make_response(jsonify(success=False, type='logout'))
        return resp     


def userNameExists(username):
    cursor.execute("""SELECT * FROM USERS WHERE USER_NAME = %s""", (username,))
    app.logger.debug(cursor._executed)
    db.commit()
    row = cursor.fetchall()
    if row:
       return True
    else:
       return False    
 
def getUsername(userId):
    cursor.execute("""SELECT USER_NAME FROM USERS WHERE USER_ID = %s""", userId)
    db.commit()
    username = cursor.fetchone()
    return username[0]

def getUserId(username):
    cursor.execute("""SELECT USER_ID FROM USERS WHERE USER_NAME = %s""", (username,))
    db.commit()
    userId = cursor.fetchone()
    return userId[0]

def getLoginStatus(userId):
   cursor.execute("""SELECT LOGGED_IN FROM USERS WHERE USER_ID = %s""", userID)
   db.commit()
   loginStatus = cursor.fetchone()
   return loginStatus 

def setLoginStatus(userId,loginStatus):
   cursor.execute("""UPDATE USERS SET LOGGED_IN = %s WHERE USER_ID = %s""",[loginStatus, userId])
   db.commit()

def dbLinksToDict(userId,col="TIME_STAMP", order="DESC" ):

   if order == "DESC":
       if col == "TIME_STAMP":
          cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s ORDER BY TIME_STAMP DESC""", userId)
       else:
          cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s ORDER BY CLICK_COUNT DESC""", userId)
   else:
        if col ==  "TIME_STAMP":
          cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s ORDER BY TIME_STAMP ASC""", userId)
        else:
          cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s ORDER BY CLICK_COUNT ASC""", userId)
   

   app.logger.debug(cursor._executed)
   db.commit()
   rows = cursor.fetchall()
   links = []
   for row in rows:
       rowDummy = {}
       rowDummy['shortUrl'] = row[1];
       rowDummy['longUrl'] = row[2];
       rowDummy['clickCount'] = row[3];
       rowDummy['timeStamp'] = row[4].strftime("%b %d, %Y at %I:%M %p")
       rowDummy['title'] = row[5]
#        app.logger.debug(rowDummy)
#        app.logger.debug(row)
       links.append(rowDummy) 
   #jsonLinks = json.dumps(links) 
   app.logger.debug(links)   
   #app.logger.debug(jsonLinks)
   return links

def get_url_title(longUrl):
        try:
                html_file = urlopen(longUrl)
                doc = html.parse(html_file).getroot()
                title=doc.xpath('/html/head/title/text()')[0]        
                title=title.decode("utf-8").encode('ascii',"ignore")
        except:
                title=longUrl
                app.logger.debug(title)
        return title


def addNewLinkToDB(userId, shortUrl, longUrl, clickCount, timeStamp):
        userId = str(MySQLdb.escape_string(userId))
        shortUrl = str(MySQLdb.escape_string(shortUrl))
        clickCount = str(MySQLdb.escape_string(str(clickCount)))
        title=get_url_title(longUrl)
        title=str(MySQLdb.escape_string(title))
        #timestamp generated at server, escape not necessary
        timeStamp = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""INSERT INTO LINKS (USER_ID, SHORT_URL, LONG_URL, CLICK_COUNT, TIME_STAMP, PAGE_TITLE) VALUES (%s, %s, %s, %s, %s, %s)""", [userId, shortUrl, longUrl, clickCount, timeStamp, title])
        app.logger.debug(cursor._executed)
        db.commit()   

def checkUniqueShortUrl(shortUrl):
    cursor.execute("""SELECT SHORT_URL FROM LINKS WHERE SHORT_URL = %s""", shortUrl)
    db.commit()
    check = cursor.fetchone()
    if check:
       return False#short url is not unique
    else:
       return True#short url is unique 

def deleteLinkFromDB(shortUrl):
    cursor.execute("""DELETE FROM LINKS WHERE SHORT_URL = %s""",shortUrl)
    db.commit()
    app.logger.debug(cursor._execute)

def addNewUserToDB( username, password, loggedIn):
     cursor.execute("""INSERT INTO USERS (USER_NAME, PASSWORD, LOGGED_IN) VALUES (%s, %s, %s)""", [username,password,loggedIn])
     app.logger.debug(cursor._executed)
     db.commit()
         

def incrementClickCountDB(shortUrl):
    cursor.execute("""UPDATE LINKS SET  CLICK_COUNT = CLICK_COUNT + 1 WHERE SHORT_URL = %s""", shortUrl)
    db.commit()

@app.route('/order', methods=['POST'])
def orderLinks():
     if 'userId' in request.cookies:
     	userId = request.cookies['userId'] 
     	col = request.form['col']
     	order = request.form['order']
     	jsonResponse = {}
     	jsonResponse['links'] =  dbLinksToDict(userId, col, order)
     	jsonResponse['success'] = True
     	resp = Response(json.dumps(jsonResponse), mimetype='application/json')
     	return resp       
     else:
	resp = make_response(jsonify(success=False))
        return resp
####
# Delete route
#
###
@app.route('/delete', methods=['POST'])
def delete():
    app.logger.debug(request.form['short_url'])
    deleteLinkFromDB(request.form['short_url'])        
    return jsonify(success=True)

###
# GET method will redirect to the short-url stored in db
# POST/PUT method will update the redirect destination
#
@app.route('/short/<name>', methods=['GET'])
def lengthen_url(name):
    """Redirects to long url or Nothing"""
    cursor.execute("""SELECT LONG_URL FROM LINKS WHERE SHORT_URL = %s""", name)
    db.commit() 
    long_url = cursor.fetchone()

    incrementClickCountDB(name)
    if not long_url:    
        return flask.redirect(url_for('error', _external=True))
    else:
        app.logger.debug("Redirecting to " + long_url[0])
        return flask.redirect(long_url[0])


@app.route('/error', methods=['GET'])
def error():
    abort(404)
    
    
@app.errorhandler(404)
def page_not_found(e):
        """Handles all requests that the server can't handle"""
        return flask.render_template("404.html", page=e)

"""
@app.route('/reset', methods=['GET'])
def reset():
    for key in db:
                del db[key]
    return flask.redirect(url_for('home', _external=True))
"""
###
# Shorten URL Resource
# should return json object user AJAX so we don't have to redirect/reload /home
###

@app.route("/shorts", methods=['PUT', 'POST'])
def shorten_url():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    #user can only add links if logged 
    if  'userId' in request.cookies:
        user_id = request.cookies['userId']   
        if user_id != "":
            short_url = str(MySQLdb.escape_string(request.form['short-url']))
            long_url = str(MySQLdb.escape_string(request.form['long-url']))
            timestamp = datetime.datetime.now()    
            click_count = 0
            title=get_url_title(long_url)
          
            #check if short url is unique 
            if checkUniqueShortUrl(short_url):
				# insert url guys to mysql database
				addNewLinkToDB(user_id, short_url, long_url, click_count, timestamp) 
				return jsonify(success=True, shortUrl=short_url, longUrl=long_url, timeStamp=timestamp, clickCount=click_count, title=title)
            else:
                return jsonify(success=False, reason="short url not unique")
        else:
            return jsonify(success=False, reason="user not logged in") 
    else:    
        #return indication that user needs to sign in operation failed
        return jsonify(success=False, reason="user not logged in")

import os
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))


    app.run(host='0.0.0.0', port=port)
