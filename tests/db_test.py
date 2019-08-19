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

        # Commit instances, all at once by just committing the event
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
        assert db_city == db_venue.city
        assert db_cat == db_ev.category
        assert db_org == db_ev.organizer
        assert db_venue == db_ev.venue

        assert db_ev in db_venue.events
        assert db_ev in db_org.events
        assert db_ev in db_cat.events
        assert db_venue in db_city.venues

def test_ondelete_cascades(app):
    """
    The system is very rigid. If any of event's foreign key objects is deleted, the event is deleted.
    For City, deletion cascades first to Venue and then to Event.
    This test check whether these cascades work correctly.
    """

    with app.app_context():
        
        # Create and commit instances
        city = _get_city()
        category = _get_category()
        organizer = _get_organizer()
        venue = _get_venue(venuecity=city)
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)
        db.session.add(event)
        db.session.commit()

        # For Category: Make sure the event exists, cascade works and the put data back
        assert Event.query.count() == 1
        db.session.delete(category)
        db.session.commit()
        assert Event.query.count() == 0
        category = _get_category()
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)
        db.session.add(event)
        db.session.commit()

        # For Venue: Make sure the event exists, cascade works and the put data back
        assert Event.query.count() == 1
        db.session.delete(venue)
        db.session.commit()
        assert Event.query.count() == 0
        venue = _get_venue(venuecity=city)
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)
        db.session.add(event)
        db.session.commit()

        # For Organizer: Make sure the event exists, cascade works and the put data back
        assert Event.query.count() == 1
        db.session.delete(organizer)
        db.session.commit()
        assert Event.query.count() == 0
        organizer = _get_organizer()
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)
        db.session.add(event)
        db.session.commit()

        # For City: Make sure the event exists and cascade works
        assert Event.query.count() == 1
        db.session.delete(city)
        db.session.commit()
        assert Event.query.count() == 0
        assert Venue.query.count() == 0

# def test_uniqueness(app):
#     """ Test model attributes that should be unique """

#     with app.app_context():

#         city = _get_city()
#         city2 = _get_city()
#         with pytest.raises(IntegrityError):
#             app.session.commit()



