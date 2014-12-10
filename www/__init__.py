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
            request.form
            raise NotImplementedError()

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
    c1u = u.Unit(args.pop('coord1unit', u.deg))
    c2u = u.Unit(args.pop('coord2unit', u.deg))

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

    comps = []
    for compnm in c.representation_component_names:
        compval = getattr(c, compnm)
        uout = c.representation_component_units.get(compnm, None)
        if uout is not None:
            compval.to(uout)
        comps.append((compnm, compval))

    output = {}
    for i, (compnm, comp) in enumerate(comps):
        ip1s = str(i + 1)
        if not isiterable(comp.value):
            val = [comp.value]
        else:
            val = comp.value
        output['coord' + ip1s] = val
        output['coord' + ip1s + 'name'] = compnm
        output['coord' + ip1s + 'unit'] = str(comp.unit)

    for fattr_nm, fattr_val in c.get_frame_attr_names().items():
        output['frame_' + fattr_nm] = str(fattr_val)

    return jsonify(output)

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404
