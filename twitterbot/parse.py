# coding: utf-8

""" Parse tweets and look for coordinates, units, etc. """

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import random

# Third-party
from astropy import log as logger
import astropy.units as u
import inflect
from nltk.tokenize import word_tokenize
import numpy as np

__all__ = ['parse_unit', 'convert_unit_tweet']

p = inflect.engine()

def parse_unit(tweet_text):
    """ Given a string block of text, find any words that can be
        interpreted as units. If the unit is preceded by a number,
        turn the pair into an Astropy Quantity. If the unit string
        is by itself, turn it into an Astropy Unit.

        Parameters
        ----------
        tweet_text : str
            A block of whitespace delimited text, e.g., a tweet.

        Returns
        -------
        units : list of :class:`astropy.units.Unit`
            A list of any bare units parsed from the text.
        quantites : list of :class:`astropy.units.Quantity`
            A list of any number+unit pairs, turned into Quantity objects.
    """

    words = word_tokenize(tweet_text)

    units = []
    quantities = []
    for i,word in enumerate(words):
        sing_word = p.singular_noun(word)
        if sing_word is False or "/" in word:
            sing_word = word

        # identify type of word
        try:
            unit = u.Unit(sing_word)
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
                units.append(unit)

        except ValueError:
            # print("error", word, sing_word)
            # print("{} not a valid unit".format(word))
            continue

    return units, quantities

def convert_unit_tweet(tweet_text, username):
    """ Given a convert command as a whitespace delimited string,
        return a string representing the returned object. For example,
        "convert 15 lightyears to parsecs" will return the string
        "4.59902090682 pc".

        Parameters
        ----------
        tweet_text : str
            A block of whitespace delimited text, e.g., a tweet.
        username : str
            The username of the person to respond to.

        Returns
        -------
        response : str
            A string response to the convert request.
    """

    try:
        units,quantities = parse_unit(tweet_text)
    except ValueError:
        # TODO: wat do?
        return None

    if len(quantities) > 1 or len(units) > 1:
        # TODO: warning?
        pass

    q = quantities[0].to(units[0])

    return "@{0} {1} {2}".format(username, q.value, q.unit)

def alternate_units(tweet_text, username):
    """ Given a tweet as a single string object, find a quantity in the
        text and return a string containing alternate units for the
        quantity.

        Parameters
        ----------
        tweet_text : str
            A block of whitespace delimited text, e.g., a tweet.
        username : str
            The username of the person to respond to.

        Returns
        -------
        response : str
            A string response containing the input quantity in alternate
            units.

    """

    # TODO: I need to define lists of preferred conversions for astronomical
    #       units for all physical types

    us,qs = parse_unit(tweet_text)

    # short circuit if the text has no quantities inside
    if len(qs) == 0:
        return None

    q = qs[0]
    eq_units = list(q.unit.find_equivalent_units())
    eq_units += list(q.unit.find_equivalent_units(units=u.imperial))
    random.shuffle(eq_units)

    alternates = list()
    for unit in eq_units[:3]:
        new_q = q.to(unit)

        # fancy stuff to get long name of units
        long_name_lens = [len(ln) for ln in new_q.unit.long_names]
        if len(long_name_lens) > 0:
            ix = np.argmax(long_name_lens)
            unit_name = new_q.unit.long_names[ix]
        else:
            unit_name = str(new_q.unit)

        # pluralize word
        if new_q.value != 1.:
            unit_name = p.plural_noun(unit_name)

        s = "{} {}".format(new_q.value, unit_name)
        alternates.append(s)

    i = 1
    s = "@{0} That's also {1}".format(username, ", ".join(alternates))
    while len(s) > 140:
        s = "@{0} That's also {1}".format(username, ", ".join(alternates[:-i]))
        i += 1

    return s
