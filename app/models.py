# -*- coding: utf-8 -*-
# pylint: disable=C0103,C0111,R0903

from datetime import datetime
from pprint import pprint
from flask_security import UserMixin, RoleMixin


from .prumap import db


class NotImportableException(Exception):
    pass

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(),
                                 db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(),
                                 db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated = db.Column(db.DateTime, default=datetime.utcnow, nullable=False,
                        onupdate=datetime.utcnow)
    name = db.Column(db.String, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String)
    active = db.Column(db.Boolean, default=False)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return '<User %r>' % self.email


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    catasto_id = db.Column(db.String(4), nullable=True)

    parent_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    parent = db.relationship('Location', remote_side=[id],
                             backref=db.backref('children', lazy=True))

    province_id = db.Column(db.String, db.ForeignKey('province.id'), nullable=False)
    province = db.relationship('Province', backref=db.backref('locations', lazy=True))

    def __init__(self, data=None):
        if data:
            #0  1   2    3    4      5      6 7 8     9      10 11     12 13 14    15    16    17    18   19     20  21   22    23  24   25
            #19;-;  081; 021 ;081021;Trapani;;5;Isole;Sicilia;-;Trapani;1;TP;81021;81021;81021;81021;L331;69.241;ITG;ITG1;ITG11;ITG;ITG1;ITG11
            #19;282;082; 053 ;082053;Palermo;;5;Isole;Sicilia;Palermo;-;1;PA;82053;82053;82053;82053;G273;657.561;ITG;ITG1;ITG12;ITG;ITG1;ITG12
            data = data.split(';')
            self.region = data[9]
            province = data[13]

            # early exclude useless data
            if (self.region not in ('Sicilia', 'Calabria', 'Puglia')) or \
               (province in ('BA', 'BT', 'FG')) \
            :
                raise NotImportableException

            pprint(data)
            pprint(type(data[5]))

            self.name = data[5].decode('iso-8859-1')
            self.province_id = data[2]
            self.catasto_id = data[18]




    def __repr__(self):
        return '<Location %r>' % self.name


class Province(db.Model):
    id = db.Column(db.String(3), primary_key=True)
    name = db.Column(db.String, nullable=False)
    shortname = db.Column(db.String(2), nullable=False)
    region = db.Column(db.Enum('Sicilia', 'Calabria', 'Puglia'), nullable=False, default='Sicilia')

    def __init__(self, data=None):
        if data:
            # 0  1   2   3     4     5  6    7    8       9       10 11 12    13    14     15 16
            # 05;ITG;ITG;ISOLE;Isole;19;ITG1;ITG1;SICILIA;Sicilia;081;-;ITG11;ITG11;Trapani;;TP;
            # 05;ITG;ITG;ISOLE;Isole;19;ITG1;ITG1;SICILIA;Sicilia;082;282;ITG12;ITG12;-;Palermo;PA;
            # pprint(data)
            data = data.split(';')
            self.region = data[9]
            self.shortname = data[16]

            # early exclude useless data
            if (self.region not in ('Sicilia', 'Calabria', 'Puglia')) or \
               (self.shortname in ('BA', 'BT', 'FG')) \
            :
                raise NotImportableException

            self.id = data[10]
            self.name = data[14]
            if data[11] != '-':
                # città metropolitane
                self.name = data[15]

    def __repr__(self):
        return '<Province %r (%r)>' % (self.name, self.region)

class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fb_id = db.Column(db.String, unique=True)
    gender = db.Column(db.Enum('M', 'F', 'Altro'), nullable=False)
    birthday = db.Column(db.Date, nullable=False)
    education = db.Column(db.String, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', backref=db.backref('volunteers', lazy=True))
    occupation_id = db.Column(db.Integer, db.ForeignKey('occupation.id'), nullable=False)
    occupation = db.relationship('Occupation', backref=db.backref('volunteers', lazy=True))

    def __repr__(self):
        return '<Volunteer %r>' % self.id

class Occupation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, data=None):
        if data:
            self.name = data.strip().decode('utf-8')

    def __repr__(self):
        return '<Occupation "%r">' % self.name

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, data=None):
        if data:
            self.name = data.strip().decode('utf-8')

    def __repr__(self):
        return '<Education "%r">' % self.name


class Source(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sentence = db.Column(db.String, nullable=False)
    expected = db.Column(db.String, nullable=True)
    datetime = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Source "%r">' % self.sentence


class Translation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('source.id'), nullable=False)
    source = db.relationship('Source', backref=db.backref('translations', lazy=True))
    author_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    author = db.relationship('Volunteer', backref=db.backref('translations', lazy=True))
    reported = db.Column(db.Boolean, default=False)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    location = db.relationship('Location', backref=db.backref('translations', lazy=True))
    sentence = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Translation "%r">' % self.sentence
