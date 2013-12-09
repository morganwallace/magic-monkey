#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
import operator
from flask import request, url_for, abort
from os import environ
from flaskext.bcrypt import Bcrypt
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
bcrypt = Bcrypt(app)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://url_shortener:4w8in43@localhost/url_shortener' 
db = SQLAlchemy(app)
#db = shelve.open("shorten.db")


###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/', methods=['GET'])
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""  
    index_title = request.args.get("title", "URL Shortener")
    #app.logger.debug(db)
    #db_sorted = sorted(db.iteritems(), key=operator.itemgetter(1))
    #app.logger.debug(db_sorted)	
    return flask.render_template(
            'home.html',
            title=index_title,
	    urls=db_sorted)

### 
# Login Resource:
#
###
@app.route('/login', methods=['GET', 'POST'])
def login():

	if request.method == 'GET':
        	return flask.render_template('login.html')
	else:
	    #if registered check username and password against db
		pass
	    #else hash password and create new row [USER_NAME, PASSWORD, LOGGED_IN]
	

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
     app.run(port=int(environ['FLASK_PORT']))
     #app.run()
