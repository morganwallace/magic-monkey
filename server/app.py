#!/usr/bin/env python

import shelve
from subprocess import check_output
import flask
from flask import request, url_for
from os import environ

app = flask.Flask(__name__)
app.debug = True

db = shelve.open("shorten.db")


###
# Home Resource:
# Only supports the GET method, returns a homepage represented as HTML
###
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    """Builds a template based on a GET request, with some default
    arguements"""
    index_title = request.args.get("title", "i253")
    hello_name = request.args.get("name", "Jim")
    return flask.render_template(
            'home.html',
            title=index_title,
            name=hello_name)



# GET method will redirect to the short-url stored in db
# POST/PUT method will update the redirect destination
###
@app.route('/short/<name>', methods=['GET'])
def lengthen_url(name):
    """Redirects to long url or Nothing"""
    destination = db.get(str(name), url_for('error'))
    app.logger.debug("Redirecting to " + destination)
    return flask.redirect(destination)

@app.route('/error', methods=['GET'])
def error():
    abort(404)
    
    
@app.errorhandler(404)
def page_not_found(e):
	"""Handles all requests that the server can't handle"""
	return flask.render_template("404.html",page=e)



@app.route("/shorts", methods=['PUT', 'POST'])
def shorten_url():
    """Set or update the URL to which this resource redirects to. Uses the
    `url` key to set the redirect destination."""
    short_url = str(request.form['short-url'])
    long_url = str(request.form['long-url'])
    db[short_url] = long_url
    return "associated " + long_url + " with  " + short_url



if __name__ == "__main__":
    app.run(port=int(environ['FLASK_PORT']),debug=True)
