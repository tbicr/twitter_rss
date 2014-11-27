import logging

from flask import Flask, request, Response, url_for, current_app, redirect
from werkzeug.contrib.atom import AtomFeed

from parser import get_tweets, get_title, get_body, get_url, get_icon


app = Flask(__name__)
app.config.from_object('settings')
app.logger.addHandler(logging.StreamHandler())
app.logger.setLevel(logging.INFO)


@app.route('/')
def home():
    return redirect(url_for('feed'))


@app.route('/timeline.atom')
def feed():
    feed = AtomFeed(app.config.get('FEED_TITLE', 'twitter'), feed_url=request.url, url=request.url_root, icon=url_for('favicon'))
    for tweet in get_tweets(current_app.config):
        feed.add(title=get_title(tweet), content=get_body(tweet), content_type='html', url=get_url(tweet),
                 published=tweet.created_at, updated=tweet.created_at)
    return feed.get_response()


@app.route('/favicon.ico')
def favicon():
    return Response(get_icon(), mimetype='image/x-icon')
