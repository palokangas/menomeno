import click
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask.cli import with_appcontext

from datetime import datetime

from menomeno import db

class Event(db.Model):
    """ Table: Event """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(250), nullable=True)
    startTime = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id"))
    organizer_id = db.Column(db.Integer, db.ForeignKey("organizer.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))

    venue = db.relationship("Venue", back_populates="events")
    organizer = db.relationship("Organizer", back_populates="event")
    category = db.relationship("Category", back_populates="events")

class Venue(db.Model):
    """ Table: Venue """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(50), nullable=True)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"))

    events = db.relationship("Event", back_populates="venue")
    city = db.relationship("City", back_populates="venues")

class Organizer(db.Model):
    """ Table: Organizer """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(50), nullable=False)

class City(db.Model):
    """ Table: City """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)

    venues = db.relationship("Venue", back_populates="city")

class Category(db.Model):
    """ Table: Category """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)

    events = db.relationship("Event", back_populates="category")

print("Modules defined")

# https://flask.palletsprojects.com/en/1.0.x/tutorial/database/
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Initialized the database.')
