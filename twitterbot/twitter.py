# coding: utf-8

from __future__ import division, print_function, unicode_literals

__author__ = "adrn <adrn@astro.columbia.edu>"
# originally written by Dan Foreman-Mackey (@dfm on GitHub)

# Standard library
import os
import time
import json

# Third-party
from astropy import log as logger
import requests
from requests_oauthlib import OAuth1

__all__ = ['tweet_stream']

env = os.environ

# Twitter API settings.
client_key = env["TW_CLIENT_KEY"]
client_secret = env["TW_CLIENT_SECRET"]
user_key = env["TW_USER_KEY"]
user_secret = env["TW_USER_SECRET"]
auth = OAuth1(client_key, client_secret, user_key, user_secret)

def tweet_stream():
    """ A generator to return tweets """

    url = "https://api.twitter.com/1.1/statuses/mentions_timeline.json"
    wait = 0

    while True:
        try:
            try:
                r = requests.get(url, auth=auth, stream=True, timeout=90)

            except requests.exceptions.ConnectionError:
                logger.warn("Tweet request failed.")
                wait = min(wait + 0.25, 16)

            else:
                code = r.status_code
                logger.warn("{0} returned: {1}".format(url, code))
                if code == 200:
                    wait = 0
                    try:
                        for line in r.iter_lines():
                            if line:
                                yield json.loads(line)

                    except requests.exceptions.Timeout:
                        logger.warn("Tweet request failed.")

                    except Exception as e:
                        logger.warn("Twitter request failed with {0}".format(e))

                elif code in [420, 429]:
                    if wait == 0:
                        wait = 60

                    else:
                        wait *= 2

                elif code in [401, 403, 404, 500]:
                    if wait == 0:
                        wait = 5

                    else:
                        wait = min(wait * 2, 320)

                else:
                    r.raise_for_status()

        except KeyboardInterrupt:
            logger.info("Exiting.")
            break

        time.sleep(wait)

def tweet_reply(text, tweet_id, user):

    url = "https://api.twitter.com/1.1/statuses/update.json"
    params = dict(status=text, in_reply_to_status_id=tweet_id)
    r = requests.post(url, data=params, auth=auth, timeout=90)

    return r.status_code
