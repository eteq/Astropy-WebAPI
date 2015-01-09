# coding: utf-8

""" Parse tweets and look for coordinates, units, etc. """

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os, sys

# Third-party
import inflect
import nltk
from nltk.tokenize import word_tokenize
import numpy as np
from astropy import log as logger
import astropy.units as u

# Project
# ...

__all__ = ['parse_unit', 'convert_unit_tweet']

p = inflect.engine()

def parse_unit(tweet_text):
    """ Search all words for valid units, check preceding number """
    words = word_tokenize(tweet_text)

    quantities = []
    for i,word in enumerate(words):
        # identify type of word
        try:
            unit = u.Unit(p.singular_noun(word))
            if unit.physical_type == 'dimensionless':
                raise ValueError()

            if i >= 1:
                value = words[i-1]

            else:
                logger.debug("Unit at start of text!")
                continue

            try:
                value = float(value)
                quantities.append(value * unit)
            except ValueError:
                # word preceding not value
                quantities.append(unit)

        except:
            # print("{} not a valid unit".format(word))
            continue

    return quantities

def convert_unit_tweet(tweet_text):

    try:
        quantity,unit = parse_unit(tweet_text)
    except ValueError:
        # TODO:
        return

    q = quantity.to(unit)

    return "{} {}".format(q.value, q.unit)
