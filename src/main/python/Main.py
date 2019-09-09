import os
import time
from twitter import *
from flask import Flask, request, render_template, redirect, abort, flash, jsonify


app = Flask(__name__)

twitter = Twitter(auth=OAuth(os.environ.get('OAUTH_TOKEN'), os.environ.get('OAUTH_SECRET'), os.environ.get('CONSUMER_KEY'), os.environ.get('CONSUMER_SECRET')))


@app.route('/search')
def search():
    # get search term from querystring 'q'
    query = request.args.get('q', '#redburns')

    # search with query term and return 10
    results = twitter.search.tweets(q=query, count=50)

    # return jsonify(results)
    # app.logger.debug(results)

    templateData = {
        'query': query,
        'tweets': results.get('statuses')
    }

    return render_template('search.html', **templateData)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# This is a jinja custom filter
@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    pyDate = time.strptime(date,'%a %b %d %H:%M:%S +0000 %Y') # convert twitter date string into python date/time
    return time.strftime('%Y-%m-%d %H:%M:%S', pyDate) # return the formatted date.


if __name__ == "__main__":
    app.debug = True

    port = int(os.environ.get('PORT', 5000))  # locally PORT 5000, Heroku will assign its own port
    app.run(host='0.0.0.0', port=port)
