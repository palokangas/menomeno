import os
import tempfile
import pytest
from datetime import datetime

from sqlalchemy.engine import Engine
from sqlalchemy import event as sqlevent # To clearly separate from Event model
from sqlalchemy.exc import IntegrityError, StatementError

from menomeno import create_app, db
from menomeno.models import Event, Venue, Category, City, Organizer

@sqlevent.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

@pytest.fixture
def app():
    """ Fixture creation modeled from course material and Flask tutorial """

    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }

    app = create_app(config)

    with app.app_context():
        db.create_all()
    
    yield app

    os.close(db_fd)
    os.unlink(db_fname)

#
# Create getters for model values with defaults
# 

def _get_city(cityname="Oulu"):
    return City(name=cityname)

def _get_category(categoryname="music"):
    return Category(name=categoryname)

def _get_organizer(orgname="Helppo Heikki",
                   orgemail="heikki@helppo.fi",
                   orgpassword="asdfASDFss"):
    return Organizer(name=orgname, email=orgemail, password=orgpassword)

def _get_venue(venuename="45 Special",
               venueurl="https://45special.com",
               venuecity=_get_city()):
    return Venue(name=venuename, url=venueurl, city=venuecity)

def _get_event(ename="Radiopuhelimet",
               edesc="Bändi soittaa",
               estartTime=datetime(2019, 8, 15, 21, 00, 00),
               evenue=_get_venue(),
               eorganizer=_get_organizer(),
               ecategory= _get_category()):

    return Event(name = ename,
                  description = edesc,
                  startTime = estartTime,
                  venue = evenue,
                  organizer = eorganizer,
                  category = ecategory)

def test_create_instances(app):
    """
    1) Create valid instance of each model and save to database
    2) Test for success of save
    3) Test relationships between models
    """

    with app.app_context():

        # Create instances
        city = _get_city()
        category = _get_category()
        organizer = _get_organizer()
        venue = _get_venue(venuecity=city)
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)

        # Commit instances
        #db.session.add(city)
        #db.session.add(category)
        #db.session.add(organizer)
        #db.session.add(venue)
        db.session.add(event)
        db.session.commit()

        # Test that instances exist
        assert City.query.count() == 1
        assert Category.query.count() == 1
        assert Organizer.query.count() == 1
        assert Venue.query.count() == 1
        assert Event.query.count() == 1

        # Check relationships
        db_ev = Event.query.first()
        db_city = City.query.first()
        db_venue = Venue.query.first()
        db_cat = Category.query.first()
        db_org = Organizer.query.first()
        assert db_city == Venue.query.first().city
        assert db_cat == db_ev.category
        assert db_cat == db_ev.organizer
        assert db_venue == db_ev.venue

        assert db_ev in db_venue.events
        assert db_ev in db_org.events
        assert db_ev in db_cat.events
        assert db_venue in db_city.venues
