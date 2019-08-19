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
    venue_id = db.Column(db.Integer, db.ForeignKey("venue.id", ondelete="CASCADE"), nullable=False)
    organizer_id = db.Column(db.Integer, db.ForeignKey("organizer.id", ondelete="CASCADE"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id", ondelete="CASCADE"), nullable=False)

    venue = db.relationship("Venue", back_populates="events")
    organizer = db.relationship("Organizer", back_populates="events")
    category = db.relationship("Category", back_populates="events")

class Venue(db.Model):
    """ Table: Venue of the Event"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(50), nullable=True)
    city_id = db.Column(db.Integer, db.ForeignKey("city.id", ondelete="CASCADE"), nullable=False)

    events = db.relationship("Event", cascade="delete", back_populates="venue")
    city = db.relationship("City", back_populates="venues")

class Organizer(db.Model):
    """ Table: Organizer of the Event"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(50), nullable=False)

    events = db.relationship("Event", cascade="delete", back_populates="organizer")

class City(db.Model):
    """ Table: City of the Venue"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    venues = db.relationship("Venue", cascade="delete", back_populates="city")

class Category(db.Model):
    """ Table: Category of the Event"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)

    events = db.relationship("Event", cascade="delete", back_populates="category")

# Command line function to initialize database
@click.command("init-db")
@with_appcontext
def init_db_command():
    db.create_all()
    click.echo('Initialized the database.')
