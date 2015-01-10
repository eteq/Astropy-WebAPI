# coding: utf-8

""" AstropyBot """

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import sqlite3

# Third-party
from astropy import log as logger

# Project
from twitterbot.twitter import tweet_stream, tweet_reply
from twitterbot.parse import convert_unit_tweet, alternate_units

conn = sqlite3.connect('tweets.db')
c = conn.cursor()
# c.execute("drop table tweets")
c.execute("""
    create table if not exists tweets (
        id serial primary key,
        tweet_id text,
        username text,
        body text,
        reply_sent integer
    )
""")

for tweet in tweet_stream():
    tweet = tweet[0]
    tweet_id = tweet['id_str']
    tweet_text = tweet['text']
    uname = tweet['user']['screen_name']

    c.execute('SELECT * FROM tweets WHERE tweet_id = "{}"'.format(tweet_id))
    row = c.fetchone()
    if row is not None and row[4] == 1:
        logger.info("Reply already sent.")
        continue

    # get responses
    try:
        conv_response = convert_unit_tweet(tweet_text, username=uname)
    except IndexError:
        conv_response = None

    alt_response = alternate_units(tweet_text, username=uname)
    if conv_response is not None:
        response = conv_response

    elif alt_response is not None:
        response = alt_response

    if response is not None:
        code = tweet_reply(response, tweet_id, uname)
    else:
        # tweet isn't relevant
        c.execute("""insert into tweets(tweet_id, username, body, reply_sent)
                      values (?, ?, ?, ?)
                  """, (tweet_id, uname, tweet_text, 1))
        continue

    if code == 200:
        sent = 1
    else:
        sent = 0
        logger.error("Failed to send reply -- error code: {}.".format(code))

    c.execute("""insert into tweets(tweet_id, username, body, reply_sent)
                  values (?, ?, ?, ?)
              """, (tweet_id, uname, tweet_text, sent))
    conn.commit()

conn.close()
