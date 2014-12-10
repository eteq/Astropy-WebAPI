# coding: utf-8
#-----------------------------------------------------------------------------
#  Copyright (C) 2014 mashta
#
#  Distributed under the terms of the BSD License.  The full license is in
#  the file LICENSE.txt, distributed as part of this software.
#-----------------------------------------------------------------------------

from __future__ import division, print_function

__author__ = "adrn <adrn@astro.columbia.edu>"

# Standard library
import os, sys
import time
import random

# Third-party
import astropy.coordinates as coord
import astropy.units as u
from astropy.coordinates.sky_coordinate import _get_frame, _get_frame_class
from flask import Flask, request, render_template, session, redirect, abort, flash, jsonify

with open(".env") as f:
    for line in f:
        key,val = line.strip().split("=")
        os.environ[key] = val

app = Flask(__name__)   # create our flask app
app.secret_key = os.environ.get('SECRET_KEY')

# @app.route('/')
# @app.route('/<tag>')
# def index(tag=None):

#     if 'instagram_access_token' in session and 'instagram_user' in session:
#         # if no tag specified, get a recent popular image, grab the tag from that
#         if tag is None:
#             while True:
#                 media = api.media_popular(1, None)

#                 if hasattr(media[0], 'tags') and len(media[0].tags) > 0:
#                     break
#                 time.sleep(0.1)

#             tag = random.choice(media[0].tags).name

#         media, next = api.tag_recent_media(2, None, tag)
#         print(next)

#         templateData = {
#             'size' : request.args.get('size','thumb'),
#             'media' : media,
#             'header' : tag.lower()
#         }

#         return render_template('display.html', **templateData)

#     else:
#         return redirect('/connect')

@app.route('/api/convert', methods=['GET', 'POST'])
def convert():
    if request.method == 'GET':
        args = dict(request.args)
        for k,v in args.items():
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
    cargs = (c1,c2)

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
    for k,v in args.items():
        if k.startswith('from_'):
            fromargs[k.split('from_')[1]] = v

        if k.startswith('to_'):
            toargs[k.split('to_')[1]] = v

    fromargs['frame'] = from_system.lower()

    # get the 'to' frame class
    ToFrame = _get_frame_class(to_system.lower())

    c = coord.SkyCoord(*cargs, unit=(c1u,c2u), **fromargs)\
             .transform_to(frame=ToFrame(**toargs))

    c1_out = c.data.lon.to(c1u).value
    c2_out = c.data.lat.to(c1u).value

    derp = dict(coord1=list(c1_out),
                coord2=list(c2_out),
                coord1unit=c1u.to_string(),
                coord2unit=c2u.to_string())

    return jsonify(derp)

# @app.errorhandler(404)
# def page_not_found(error):
#     return render_template('404.html'), 404
