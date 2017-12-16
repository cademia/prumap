# -*- coding: utf-8 -*-

import flask

from models import *
from flask_sqlalchemy import SignallingSession
from .prumap import db, view
import logging

# module imports
# ...
# ...

class Manager(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        db.create_all()
        self.session = SignallingSession(db)

    @view()
    def index(self):
        return {}
