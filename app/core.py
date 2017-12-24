# -*- coding: utf-8 -*-

import flask

from models import *
from flask_sqlalchemy import SignallingSession
from flask_security import login_required
from sqlalchemy.exc import IntegrityError
from .prumap import app, db, view
import logging

# module imports
# ...
# ...

from . import fbhelper

class Manager(object):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        db.create_all()
        self.session = SignallingSession(db)
        self.app = app

        self.fb = fbhelper.FBHelper(self)

    @view()
    @login_required
    def index(self):
        return {}

    # Create a user to test with
    @app.before_first_request
    def create_user():
        from .prumap import user_datastore
        try:
            user_datastore.create_user(email='admin@local', password='admin', active=True)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
