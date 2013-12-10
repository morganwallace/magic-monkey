#!/usr/bin/env python

from subprocess import check_output
import flask
import operator
from flask import request, url_for, abort, jsonify
from os import environ
from flaskext.bcrypt import Bcrypt
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.gzip import Gzip
from flask import Flask
from flask.ext.compress import Compress
from flask import request
from flask import make_response
import MySQLdb
import datetime

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
    userId = request.cookies.get('userId')
    """Builds a template based on a GET request, with some default
    arguements"""  
    if request.method == 'GET':
    	username = request.cookies.get('username')
        index_title = request.args.get("title", "URL Shortener")
        #app.logger.debug(db)
        #db_sorted = sorted(db.iteritems(), key=operator.itemgetter(1))
        #app.logger.debug(db_sorted)        
        return flask.render_template(
            'home.html',
            title=index_title)
    else:
        username = str(MySQLdb.escape_string(request.form['username']))
        password = str(MySQLdb.escape_string(request.form['password']))

        if request.form['form_type'] == 'signup':
		signup(username, password)
			
		#set cookie
		resp = make_response(flask.render_template('home.html'))
		resp.set_cookie('username', username)
		return resp
        else:
            login(username, password)
        return flask.render_template('home.html')


### 
# Signup Resource:
# use AJAX, should return json or write values in the http response
# set userId in cookie once user record created if username not unique return false
###

@app.route('/signup', methods=['POST'])
def signup(username, password):
     
     #check if username exists
     cursor.execute("""SELECT * FROM USERS WHERE USER_NAME = %s""", username)
     app.logger.debug(cursor._executed)
     db.commit()
     row = cursor.fetchall()
     app.logger.debug(row)
     if not row:
         #create new row in table USERS 
         pw_hash = bcrypt.generate_password_hash(password)     
         newEntry = [username, str(pw_hash), 1]
         app.logger.debug("signup button clicked")
         app.logger.debug(newEntry)
         cursor.execute("""INSERT INTO USERS (USER_NAME, PASSWORD, LOGGED_IN) VALUES (%s, %s, %s)""", newEntry)
         app.logger.debug(cursor._executed)
         db.commit()
         app.logger.debug("Signup successful")
         return True
     else:
         app.logger.debug("Username already created")
         return flask.response.write(False)
"""
basic setting a cookie example useing flask

    resp = make_response(render_template(...))
    resp.set_cookie('username', 'the username')
    return resp
"""

### 
# Login Resource:
# use AJAX, should return json or write values in the http response
# 
###

@app.route('/login', methods=['POST'])
def login(username, password):

     app.logger.debug("login button clicked")
     #check for existing user record in table USERS 
     
     cursor.execute("""SELECT * FROM USERS WHERE USER_NAME = %s""", username )
     app.logger.debug(cursor._executed)
     db.commit()

     row = cursor.fetchone()
     app.logger.debug(row) 
     pw_hash = row[2]
     app.logger.debug(pw_hash)  
     if row:
         pass
         #check if password matches
         if bcrypt.check_password_hash(pw_hash, password): 
             app.logger.debug("password found")
             #setLoginStatus(userId, 1)
             return True
         else:
             app.logger.debug("password not found")
             return False
     else:
         app.logger.debug("username not found in database")
         return False


def getLoginStatus(userId):
   cursor.execute("""SELECT LOGGED_IN FROM USERS WHERE USER_ID = %s""", userID)
   db.commit()
   loginStatus = cursor.fetchone()
   return loginStatus 

def setLoginStatus(userId,loginStatus):
   cursor.execute("""INSERT INTO USERS (LOGGED_IN) VALUES (%s)""",loginStatus)
   db.commit()

def dbLinksToJSON(userId):
   urls = {}
   cursor.execute("""SELECT * FROM LINKS WHERE USER_ID = %s""", userID);
   app.logger.debug(cursor._executed)
   db.commit()
   rows = cursor.fetchall()
   for row in rows:
       app.logger.debug(row)
       pass#construct urls to pass to home.html templete for rendering
   return urls

def addNewLinkToDB(userId, shortUrl, longUrl, clickCount, timeStamp):
    cursor.execute("""INSERT INTO LINKS (USER_ID, SHORT_URL, LONG_URL, CLICK_COUNT, TIME_STAMP) VALUES (%s, %s, %s, %s, %s)""", userID, shortUrl, longUrl, clickCount, timeStamp)
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

@app.route("/shorts", methods=['PUT', 'POST'])
def shorten_url():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    #if  user is logged in
        user_id = ""#get user id from cookie?   
        short_url = str(request.form['short-url'])
        long_url = str( request.form['long-url'])
        timestamp = datetime.datetime.now()    
        click_count = 0
        addNewLinkToDB(user_id, short_url, long_url, timestamp, click_count) 

    #else    
    # insert url guys to mysql database
    # // item =  len(db), long_url
    # // db[short_url] = item
    #app.logger.debug(url_for('home', _external=True))
    
    #should return json object user AJAX so we don't have to redirect/reload /home
    return flask.redirect(url_for('home', _external=True))
    #"""return "associated " + long_url + " with  " + short_url"""



if __name__ == "__main__":
     #session = loadSession()
     #res = session.query(Users).all()
     #res[1]
     app.run(port=int(environ['FLASK_PORT']))
     #app.run()
