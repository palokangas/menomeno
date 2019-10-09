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
    """
    Creates dummy data for database elements
    """

    category = Category(name="music")

    for i in range(1, 3):
        city = City(name=f"city{i}")
        db.session.add(city)
        db.session.commit()

        for j in range(1, 3):
            venue = Venue(name=f"venuename{i}-{j}", url=f"https://venue{i}{j}.com", city=city)
            organizer = Organizer(name=f"organizer{j}", email=f"organizer{i}{j}@helppo.fi", password="asASDdfa5")
            db.session.add(venue)
            db.session.add(organizer)
            db.session.commit()

            for k in range(1, 3):

                event = Event(name = f"event-{i}-{j}-{k}",
                            description = f"{i}{j}{k} band on tour",
                            startTime = datetime(2019, i, j, 21, k, 00),
                            venue = venue,
                            organizer = organizer,
                            category = category)
                event.set_url()

                db.session.add(event)
                try:
                    db.session.commit()
                except:
                    print("Commit failed. Rolling back.")
                    db.session.rollback()

@click.command("populate-models")
@with_appcontext
def populate():
    populate_models()
