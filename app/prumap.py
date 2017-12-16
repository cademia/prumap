# -*- coding: utf-8 -*-

import flask

import logging
import logging.handlers
from beaker.middleware import SessionMiddleware
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from functools import wraps
from werkzeug.routing import BaseConverter
from pprint import pprint


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
       super(RegexConverter, self).__init__(url_map)
       self.regex = items[0]

app = flask.Flask('prumap')
app.config.from_object('config')
db = SQLAlchemy(app)

app.url_map.converters['re'] = RegexConverter

session_opts = {
    'session.type': 'cookie',
    'session.validate_key': True,
    'session.cookie_expires': True,
    'session.timeout': 3600 * 24, # 1 day
    'session.encrypt_key': '0a9138da42c0118bce6ecd17fd9a8f90',
}
app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
handler = logging.FileHandler('logs/application.log')
formatter = logging.Formatter('%(name)s:%(asctime)s:%(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#urlliblog = logging.getLogger('urllib3.connectionpool')
#urlliblog.setLevel(logging.WARNING)
#urlliblog = logging.getLogger('requests.packages.urllib3.connectionpool')
#urlliblog.setLevel(logging.WARNING)

def view(template=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            template_name = template
            if template_name is None:
                template_name = flask.request.endpoint.replace('.', '/') + '.html'
            ctx = f(*args, **kwargs)
            if ctx is None:
                ctx = {}
            elif not isinstance(ctx, dict):
                return ctx
            return flask.render_template(template_name, **ctx)
        return decorated_function
    return decorator


import models

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore)

import core
manager = core.Manager()

from routes import *
