# coding: utf-8

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os

# Third-party
import astropy.time as at
import astropy.units as u
from astropy.utils import isiterable
import numpy as np
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

# This package
from . import app

def _parse_args(args):
    value = np.atleast_1d(args['value']).astype(float)

    from_format = args['from_format']
    from_scale = args['from_scale']
    to_format = args.get('to_format', from_format)
    to_scale = args.get('to_scale', from_scale)

    output = dict()
    t = at.Time(value, scale=from_scale, format=from_format)
    output['value'] = list(getattr(getattr(t, to_scale), to_format))

    return output

@app.route('/time/', methods=['GET','POST'])
def time_index():
    return render_template('time-index.html')

@app.route('/time/convert', methods=['GET', 'POST'])
def time_convert():
    if request.method == 'GET':
        args = dict(request.args)
        for k, v in args.items():
            if len(v) == 1:
                args[k] = v[0]

    elif request.method == 'POST':
        json = request.get_json()
        if json is not None:
            args = dict(json)

        else:
            raise NotImplementedError()

    return jsonify(_parse_args(args))
