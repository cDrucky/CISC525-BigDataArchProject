from flask import Flask, request, redirect, url_for, session, g, flash, render_template
import urllib.parse as urlparse
import sys
sys.modules["urlparse"] = urlparse
sys.modules["urllib"] = urlparse
from flask_oauth import OAuth

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# configuration
SECRET_KEY = 'Hiy9Qm4Jv731kdMqNEQ9ZPnArGiFFDswZSJEMkJOKAp5e '
DEBUG = True

# setup flask
app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

# Use Twitter as example remote application
twitter = oauth.remote_app('twitter',
# unless absolute urls are used to make requests, this will be added
# before all URLs.  This is also true for request_token_url and others.
base_url='https://api.twitter.com/1/',
# where flask should look for new request tokens
request_token_url='https://api.twitter.com/oauth/request_token',
# where flask should exchange the token with the remote application
access_token_url='https://api.twitter.com/oauth/access_token',
# twitter knows two authorization URLs.  /authorize and /authenticate.
# they mostly work the same, but for sign on /authenticate is
# expected because this will give the user a slightly different
# user interface on the twitter side.
authorize_url='https://api.twitter.com/oauth/authenticate',
# the consumer keys from the twitter application registry.
consumer_key='2Ax5E92dSyOZrOzdqHKrxoNOp',
consumer_secret='HaNGeo6JcGWcSVhqIulZnA099ShTgFpPAb28tltGUbHsRwotJa'
)

@twitter.tokengetter
def get_twitter_token(token=None):
    return session.get('twitter_token')

@app.route('/')
def index():
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))

    access_token = access_token[0]

    return render_template('index.html')

@app.route('/login')
def login():
    return twitter.authorize(callback=url_for('oauth_authorized',

next=request.args.get('next') or request.referrer or None))

@app.route('/logout')
def logout():
    session.pop('screen_name', None)
    flash('You were signed out')
    return redirect(request.referrer or url_for('index'))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash(u'You denied the request to sign in.')
        return redirect(next_url)

    access_token = resp['oauth_token']
    session['access_token'] = access_token
    session['screen_name'] = resp['screen_name']

    session['twitter_token'] = (
    resp['oauth_token'],
    resp['oauth_token_secret']
    )

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()