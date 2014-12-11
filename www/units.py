# coding: utf-8

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os

# Third-party
import astropy.units as u
from astropy.utils import isiterable
import numpy as np
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

# This package
from . import app

def _parse_args(args):
    v = np.atleast_1d(args['value']).astype(float)
    from_unit = u.Unit(args['from'])
    to_unit = u.Unit(args['to'])

    output = dict()
    output['value'] = (v*from_unit).to(to_unit).value.tolist()
    output['unit'] = args['to']

    return output

@app.route('/units/', methods=['GET','POST'])
def units_index():
    return render_template('units-index.html')

@app.route('/units/convert', methods=['GET', 'POST'])
def units_convert():
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
