#!/usr/bin/env python

from subprocess import check_output
import flask
import operator
from flask import request, url_for, abort
from os import environ
from flaskext.bcrypt import Bcrypt
from flask import Flask
import MySQLdb

app = flask.Flask(__name__)
bcrypt = Bcrypt(app)
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
        #app.logger.debug(db)
        #db_sorted = sorted(db.iteritems(), key=operator.itemgetter(1))
        #app.logger.debug(db_sorted)	
        return flask.render_template(
            'home.html',
            title=index_title)
    else:
        if request.form['form_type'] == 'signup':
            username = str(MySQLdb.escape_string(request.form['username']))
            password = str(MySQLdb.escape_string(request.form['password']))
            signup(username, password)
        else:
            pass
        return flask.render_template('home.html')

### 
# Login Resource:
#
###
#@app.route('/login', methods=['GET', 'POST'])
def signup(username, password):

     #create new row in table USERS 
     pw_hash = bcrypt.generate_password_hash(password)     
     newEntry = [username, str(pw_hash), 1]
     app.logger.debug("signup button clicked")
     app.logger.debug(newEntry)
     cursor.execute("""INSERT INTO USERS (USER_NAME, PASSWORD, LOGGED_IN) VALUES (%s, %s, %s)""", newEntry)
     app.logger.debug(cursor._executed)
     db.commit()

def login(username, password):

     #check for existing user record in table USERS 
     
     cursor.execute("""SELECT PASSWORD FROM USERS WHERE USER_NAME = %s""", username )
     pw_hash = cursor.fetchall()
     app.logger.debug(pw_hash)  
     if bcrypt.check_password_hash(password, pw_hash):
         newEntry = [username, str(pw_hash), 1]
         app.logger.debug("login button clicked")
         app.logger.debug(newEntry)
         cursor.execute("""INSERT INTO USERS (USER_NAME, PASSWORD, LOGGED_IN) VALUES (%s, %s, %s)""", newEntry)
         app.logger.debug(cursor._executed)
         db.commit()

###
# GET method will redirect to the short-url stored in db
# POST/PUT method will update the redirect destination
#
@app.route('/short/<name>', methods=['GET'])
def lengthen_url(name):
    """Redirects to long url or Nothing"""
    """
    if not db.has_key(str(name)):    
	return flask.redirect(url_for('error', _external=True))
    else:
	destination = db.get(str(name))
	app.logger.debug("Redirecting to " + destination[1])
	return flask.redirect(destination[1])
    """

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
    short_url = str(request.form['short-url'])
    long_url = str( request.form['long-url'])
    # insert url guys to mysql database
    # // item =  len(db), long_url
    # // db[short_url] = item
    #app.logger.debug(url_for('home', _external=True))
    return flask.redirect(url_for('home', _external=True))
    #"""return "associated " + long_url + " with  " + short_url"""



if __name__ == "__main__":
     #session = loadSession()
     #res = session.query(Users).all()
     #res[1]
     app.run(port=int(environ['FLASK_PORT']))
     #app.run()
