# -*- coding: utf-8 -*-

#from bottle import hook, route, post, error, redirect, HTTPError, request
from pprint import pprint
from ..prumap import manager, app

@app.route('/')
def index():
    return manager.index()

#@app.route('/<re("js|css|img"):path>/<filename>')
#def static(path, filename):
#    return manager.static(path, filename)
