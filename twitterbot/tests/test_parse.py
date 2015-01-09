# coding: utf-8

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os
import sys

# Third-party
import numpy as np
import pytest

from ..parse import parse_unit, convert_unit_tweet

def test_parse_units():
    tweet = "This star is 15 lightyears away! http://t.co/kmsdfkn"
    print(parse_unit(tweet))

    tweet = "Convert 15 lightyears to parsecs"
    print(parse_unit(tweet))

def test_convert_tweet():
    tweet = "Convert 15 lightyears to parsecs"
    print(convert_unit_tweet(tweet))

    tweet = "Convert 15 minutes to picoseconds"
    print(convert_unit_tweet(tweet))



