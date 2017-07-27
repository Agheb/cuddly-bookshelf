#!/bin/env python

from bookshelf import db
from bookshelf.views import User, Genre, Item

db.session.remove()
db.create_all()
genre_ls = ['Science fiction', 'Science', 'Drama',
            'Psychology', 'Romance',
            'Computer Science', 'Children', 'Self help']

x = Genre(name="Science fiction")
db.session.add(x)
print 'Genre added'
db.session.commit()


"""
for genre in genre_ls:
    x = Genre()
    x.name = genre
    db.session.add(x)
    print 'Genre: %s added' % genre
    db.session.commit()
"""
print 'Done'
