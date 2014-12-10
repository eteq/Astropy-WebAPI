# coding: utf-8
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 darn + eteq
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file LICENSE.txt, distributed as part of this software.
#-----------------------------------------------------------------------------

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os

# Third-party
import astropy.units as u
from astropy.utils import isiterable
from astropy.coordinates import SkyCoord, frame_transform_graph
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

with open(".env") as f:
    for line in f:
        key, val = line.strip().split("=")
        os.environ[key] = val

app = Flask(__name__)   # create our flask app
app.secret_key = os.environ.get('SECRET_KEY')

def _parse_args(args):
    # first try pulling out separate coordinates
    c1 = args.pop('coord1', None)
    c2 = args.pop('coord2', None)
    cargs = (c1, c2)

    # if either are None, check for a coordstr
    if c1 is None or c2 is None:
        coordstr = args.pop('coordstr', None)
        cargs = (coordstr,)

    if (c1 is None or c2 is None) and (coordstr is None):
        # TODO: throw a error
        raise ValueError("Shitty arguments, yo.")

    # default units are degrees
    c1u = u.Unit(args.pop('coord1unit', 'degree'))
    c2u = u.Unit(args.pop('coord2unit', 'degree'))

    to_system = args.pop('to')
    from_system = args.pop('from')

    # extra arguments to pass to the coordinate frames
    fromargs = dict()
    toargs = dict()
    for k, v in args.items():
        if k.startswith('from_'):
            fromargs[k.split('from_')[1]] = v

        if k.startswith('to_'):
            toargs[k.split('to_')[1]] = v

    fromargs['frame'] = from_system.lower()

    # get the 'to' frame class
    ToFrame = frame_transform_graph.lookup_name(to_system.lower())

    c = SkyCoord(*cargs, unit=(c1u, c2u), **fromargs).transform_to(frame=ToFrame(**toargs))

    c1_out = c.data.lon.to(c1u).value
    c2_out = c.data.lat.to(c1u).value

    if not isiterable(c1_out):
        c1_out = [c1_out]
        c2_out = [c2_out]

    return dict(coord1=list(c1_out),
                coord2=list(c2_out),
                coord1unit=c1u.to_string(),
                coord2unit=c2u.to_string())

@app.route('/', methods=['GET','POST'])
def index():

    if request.method == 'POST':
        args = dict()
        lines = request.form['input-coordinates'].split('\r\n')
        args['coord1'] = [line.split()[0] for line in lines]
        args['coord2'] = [line.split()[1] for line in lines]
        args['to'] = 'icrs'
        args['from'] = 'galactic'

        derp = _parse_args(args)
        return render_template('index.html', outputCoords=zip(derp['coord1'],derp['coord2']))

    return render_template('index.html', outputCoords=None)

@app.route('/api/convert', methods=['GET', 'POST'])
def convert():
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
            args = dict()
            lines = request.form['input-coordinates'].split('\r\n')
            args['coord1'] = [line.split()[0] for line in lines]
            args['coord2'] = [line.split()[1] for line in lines]
            args['to'] = 'icrs'
            args['from'] = 'galactic'

    derp = _parse_args(args)
    for fattr_nm, fattr_val in c.get_frame_attr_names().items():
        derp['frame_' + fattr_nm] = str(fattr_val)

    return jsonify(derp)

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404
