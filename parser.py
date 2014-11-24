from __future__ import unicode_literals

from flask import current_app
import requests
import tweepy


def get_tweets(config):
    auth = tweepy.OAuthHandler(config['CONSUMER_KEY'], config['CONSUMER_SECRET'])
    auth.set_access_token(config['ACCESS_TOKEN'], config['ACCESS_TOKEN_SECRET'])
    api = tweepy.API(auth)
    return api.home_timeline(count=200, exclude_replies=False, include_entities=True)


def get_title(tweet):
    return '{} (@{}): {}'.format(tweet.author.name, tweet.author.screen_name, tweet.text[:50])


def get_body(tweet):
    if getattr(tweet, 'retweeted_status', None):
        template = ('retweeted <a href="https://twitter.com/{tweet.author.screen_name}">'
                        '<img src="{tweet.author.profile_image_url}"/>'
                        '{tweet.author.name} (@{tweet.author.screen_name})'
                    '</a>:<br/>'
                    '<blockqoute>'
                        '<a href="https://twitter.com/{tweet.retweeted_status.author.screen_name}">'
                            '<img src="{tweet.retweeted_status.author.profile_image_url}"/>'
                            '{tweet.retweeted_status.author.name} (@{tweet.retweeted_status.author.screen_name})'
                        '</a>:<br/>'
                        '{body}'
                    '</blockqoute>')
        body = tweet.retweeted_status.text
    else:
        template = ('<a href="https://twitter.com/{tweet.author.screen_name}">'
                        '<img src="{tweet.author.profile_image_url}"/>'
                        '{tweet.author.name} (@{tweet.author.screen_name})'
                    '</a>:<br/>{body}')
        body = tweet.text

    for symbol in tweet.entities.get('symbols', []):
        current_app.logger.info('tweet replacing: symbol: {}'.format(symbol))
    for hashtag in tweet.entities.get('hashtags', []):
        body = body.replace('#' + hashtag['text'],
                            '<a href="https://twitter.com/hashtag/{0}?src=hash">#{0}</a>'.format(hashtag['text']))
    for mention in tweet.entities.get('user_mentions', []):
        body = body.replace('@' + mention['screen_name'],
                            '<a href="https://twitter.com/{0}">{1} (@{0})</a>'.format(mention['screen_name'],
                                                                                      mention['name']))
    for url in tweet.entities.get('urls', []):
        body = body.replace(url['url'],
                            '<a href="{0}">{0}</a>'.format(url['expanded_url']))
    for media in tweet.entities.get('media', []):
        if media['type'] in ('image', 'photo'):
            body = body.replace(media['url'],
                                '<br/><img src="{}"/>'.format(media['media_url']))
        else:
            current_app.logger.info('tweet replacing: media: {}'.format(media))

    extra_keys = set(tweet.entities.keys()) - {'hashtags', 'symbols', 'user_mentions', 'urls', 'media'}
    if extra_keys:
        current_app.logger.info('tweet replacing: other: {}'.format(extra_keys))

    return template.format(tweet=tweet, body=body)


def get_url(tweet):
    return 'https://twitter.com/{}/status/{}'.format(tweet.author.screen_name, tweet.id)


def get_icon():
    return requests.get('https://g.twimg.com/Twitter_logo_blue.png').content
