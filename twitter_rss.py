import logging.handlers

from flask import Flask, request, Response, url_for, current_app, redirect
from werkzeug.contrib.atom import AtomFeed

from parser import get_tweets, get_title, get_body, get_url, get_icon


app = Flask(__name__)
app.config.from_object('settings')

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.INFO)
app.logger.addHandler(stream_handler)

smtp_handler = logging.handlers.SMTPHandler(**app.config.ERROR_EMAIL)
smtp_handler.setLevel(logging.ERROR)
app.logger.addHandler(smtp_handler)


@app.route('/')
def home():
    return redirect(url_for('feed'))


@app.route('/timeline.atom')
def feed():
    feed = AtomFeed(app.config.get('FEED_TITLE') or 'twitter', feed_url=request.url, url=request.url_root, icon=url_for('favicon'))
    for tweet in get_tweets(current_app.config):
        feed.add(title=get_title(tweet), content=get_body(tweet), content_type='html', url=get_url(tweet),
                 published=tweet.created_at, updated=tweet.created_at)
    return feed.get_response()


@app.route('/favicon.ico')
def favicon():
    return Response(get_icon(), mimetype='image/x-icon')
