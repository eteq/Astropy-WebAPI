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

with open(".env") as f:
    for line in f:
        key, val = line.strip().split("=")
        os.environ[key] = val

app = Flask(__name__)   # create our flask app
app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

import coordinates
