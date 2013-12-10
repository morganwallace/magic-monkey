#!/usr/bin/env python

from subprocess import check_output
import flask
import operator
from flask import request, url_for, abort, jsonify, Flask, Response, make_response
from os import environ
from flaskext.bcrypt import Bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.gzip import Gzip
from flask.ext.compress import Compress
import MySQLdb
import datetime
import json

app = flask.Flask(__name__)
Compress(app)
bcrypt = Bcrypt(app)
# gzip = Gzip(app)

app.debug = True
db=MySQLdb.connect(host="localhost",user="url_shortener",
                  passwd="4w8in43",db="url_shortener")
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
        index_title = request.args.get("title", "URL Shortener")
        return flask.render_template(
            'home.html',
            title=index_title)

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
         resp = make_response(jsonify(success=False))
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
             #setLoginStatus(userId, 1)
	     jsonResponse = {}
             jsonResponse['links'] =  dbLinksToDict(str(row[0]))
             jsonResponse['success'] = True
             
             resp = Response(json.dumps(jsonResponse), mimetype='application/json')
             #resp = jsonify(success=True, username=username, links=jsonLinks))
	     resp.set_cookie('userId', str(row[0]))
	     return resp
         else:
             app.logger.debug("password not found")
	     return make_response(jsonify(success=False, reason="bad password"))
     else:
         app.logger.debug("username not found in database")
         return make_response(jsonify(success=False, reason="bad username"))

####
# Logout
#
###

@app.route('/logout', methods=['POST'])
def logout():
    if 'userId' in request.cookies:
        resp = make_response(jsonify(success=True, type='logout'))
        resp.set_cookie('userId', '')
        return resp
    else:
        resp = make_response(jsonify(success=False, type='logout'))
        return resp     


def userNameExists(username):
    cursor.execute("""SELECT * FROM USERS WHERE USER_NAME = %s""", username)
    app.logger.debug(cursor._executed)
    db.commit()
    row = cursor.fetchall()
    if row:
       return True
    else:
       return False    
 

def getUserId(username):
    cursor.execute("""SELECT USER_ID FROM USERS WHERE USER_NAME = %s""", username)
    db.commit()
    userId = cursor.fetchone()
    return userId[0]

def getLoginStatus(userId):
   cursor.execute("""SELECT LOGGED_IN FROM USERS WHERE USER_ID = %s""", userID)
   db.commit()
   loginStatus = cursor.fetchone()
   return loginStatus 

def setLoginStatus(userId,loginStatus):
   cursor.execute("""INSERT INTO USERS (LOGGED_IN) VALUES (%s)""",loginStatus)
   db.commit()

def dbLinksToDict(userId):
   cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s""", userId);
   app.logger.debug(cursor._executed)
   db.commit()
   rows = cursor.fetchall()
   links = []
   for row in rows:
       rowDummy = {}
       rowDummy['shortUrl'] = row[1];
       rowDummy['longUrl'] = row[2];
       rowDummy['clickCount'] = row[3];
       rowDummy['timeStamp'] = row[4].strftime("%Y-%d-%m %H:%M:%S")
       app.logger.debug(rowDummy)
       app.logger.debug(row)
       links.append(rowDummy) 
   #jsonLinks = json.dumps(links) 
   app.logger.debug(links)   
   #app.logger.debug(jsonLinks)
   return links

def addNewLinkToDB(userId, shortUrl, longUrl, clickCount, timeStamp):
    userId = str(MySQLdb.escape_string(userId))
    shortUrl = str(MySQLdb.escape_string(shortUrl))
    clickCount = str(MySQLdb.escape_string(str(clickCount)))
    #timestamp generated at server, escape not necessary
    timeStamp = timeStamp.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""INSERT INTO LINKS (USER_ID, SHORT_URL, LONG_URL, CLICK_COUNT, TIME_STAMP) VALUES (%s, %s, %s, %s, %s)""", [userId, shortUrl, longUrl, clickCount, timeStamp])
    db.commit()   

def addNewUserToDB( username, password, loggedIn):
     cursor.execute("""INSERT INTO USERS (USER_NAME, PASSWORD, LOGGED_IN) VALUES (%s, %s, %s)""", [username,password,loggedIn])
     app.logger.debug(cursor._executed)
     db.commit()
         

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

    if not long_url:    
	return flask.redirect(url_for('error', _external=True))
    else:
	app.logger.debug("Redirecting to " + long_url)
	return flask.redirect(long_url)


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
    if  'userId' in request.cookies:
        user_id = request.cookies['userId']   
        if user_id != "":
            short_url = str(request.form['short-url'])
            long_url = str( request.form['long-url'])
            timestamp = datetime.datetime.now()    
            click_count = 0
        
            # insert url guys to mysql database
            addNewLinkToDB(user_id, short_url, long_url, click_count, timestamp) 
            return jsonify(succss=True, shortUrl=short_url, longUrl=long_url, timeStamp=timestamp, clickCount=click_count)
        else:
            return jsonify(success=False, reason="user not logged in") 
    else:    
        #return indication that user needs to sign in operation failed
	return jsonify(success=False, reason="user not logged in")


if __name__ == "__main__":
     app.run(port=int(environ['FLASK_PORT']))
