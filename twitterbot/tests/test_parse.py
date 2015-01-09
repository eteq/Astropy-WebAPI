# coding: utf-8

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Third-party
import astropy.units as u

from ..parse import parse_unit, convert_unit_tweet

convert_tweets = ["Convert 15 lightyears to parsecs",
                  "Convert 15 km/s to pc/Myr"]
expected = [(u.parsec, 15.*u.lightyear),
            (u.pc/u.Myr, 15*u.km/u.s)]
def test_parse_unit():

    # ---
    tweet = "This star is 15 lightyears away! http://t.co/kmsdfkn"
    us,qs = parse_unit(tweet)
    assert len(us) == 0
    assert len(qs) == 1
    assert qs[0] == u.Quantity(15.*u.lightyear)

    # ---
    for i,tweet in enumerate(convert_tweets):
        us,qs = parse_unit(tweet)
        assert len(us) == 1
        assert len(qs) == 1
        assert us[0] == expected[i][0]
        assert qs[0] == expected[i][1]

def test_convert_unit_tweet():
    for i,tweet in enumerate(convert_tweets):
        resp = convert_unit_tweet(tweet)
        q = expected[i][1].to(expected[i][0])
        expected_resp = "{} {}".format(q.value, q.unit)
        assert resp == expected_resp
