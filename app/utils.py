# -*- coding: utf-8 -*-

"""
Generic utilities for dealing with the database.
"""

import os
from pprint import pprint
from .prumap import manager, models

def populate_generic(source, class_):
    """ Generic function calling class_(source) for each line in source. """
    with open(os.path.join('data', source), 'r') as data:
        for line in data.readlines():
            # pprint(line)
            try:
                obj = class_(line.strip())
            except models.NotImportableException:
                continue
            manager.session.add(obj)
        manager.session.commit()

def populate_database():
    """ Populate the database with initial data. """
    populate_generic('occupations.txt', models.Occupation)
    populate_generic('education.txt', models.Education)
    populate_generic('comuni_20170630.csv', models.Location)
    populate_generic('province.csv', models.Province)
