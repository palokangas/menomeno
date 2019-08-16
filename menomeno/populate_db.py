# Very rudimentary populate script. Just creates a single entry in each table.

import click
from flask.cli import with_appcontext
from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy import event as sqlevent # Just to separate from Event model
from sqlalchemy.exc import IntegrityError, StatementError

from menomeno import db
from menomeno.models import Event, City, Category, Venue, Organizer


def add_city(name):
    pass

def add_venue():
    pass

def populate_models():
    city = City(name="Oulu")
    category = Category(name="music")
    venue = Venue(name="45 Special", url="https://45cpecial.com", city=city)
    organizer = Organizer(name="Helppo Heikki", email="heikki@helppo.fi", password="asASDdfa5")
    event = Event(name = "Bunnyrabbits",
                  description = "New band on tour",
                  startTime = datetime(2019, 8, 15, 21, 00, 00),
                  venue = venue,
                  organizer = organizer,
                  category = category)

    db.session.add(event)
    try:
        db.session.commit()
    except:
        print("Commit failed. Rolling back.")
        db.session.rollback()

    print(event)

@click.command("populate-models")
@with_appcontext
def populate():
    populate_models()

