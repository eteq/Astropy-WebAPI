# coding: utf-8

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os

# Third-party
import astropy.units as u
from astropy.utils import isiterable
from astropy.coordinates import SkyCoord, frame_transform_graph
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

# This package
from . import app

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
        # container for information for this coordinate
        this_coord = dict()

        ip1s = str(i + 1)
        if not isiterable(comp.value):
            val = [comp.value]
        else:
            val = comp.value

        this_coord['data'] = list(val)
        this_coord['name'] = compnm
        this_coord['unit'] = str(comp.unit)
        output['coord' + ip1s] = this_coord

    for fattr_nm in c.get_frame_attr_names():
        output['frame_' + fattr_nm] = str(getattr(c, fattr_nm))

    return output

@app.route('/coordinates/', methods=['GET','POST'])
def index():
    frame_names = frame_transform_graph.get_names()
    return render_template('coordinates-index.html', frame_names=frame_names)

@app.route('/coordinates/convert', methods=['GET', 'POST'])
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
            lines = request.form['input-coordinates'].split('\r\n');
            args['coord1'] = [float(line.split()[0]) for line in lines];
            args['coord2'] = [float(line.split()[1]) for line in lines];
            args['from'] = request.form['from'];
            args['to'] = request.form['to'];

    return jsonify(_parse_args(args))

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404
