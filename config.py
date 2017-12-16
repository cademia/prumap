from os import path

# this is where the real secrets are, not keeping it in git
from localconfig import *

# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DEBUG = True

# Database details
SQLALCHEMY_DATABASE_URI = '{0}{1}'.format('sqlite:///',
                                          path.join(BASE_DIRECTORY, 'app.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
