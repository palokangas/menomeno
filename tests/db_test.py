# These test omit length check because of sqlite limitations

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

# Create getters for model values with parameters and defaults 
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

def test_uniqueness(app):
    """
    Test model attributes that should be unique:
    city name, category name and organizer email
    """

    with app.app_context():

        city1 = _get_city()
        city2 = _get_city()
        db.session.add(city1)
        db.session.add(city2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        organizer1 = _get_organizer(orgemail="t@p.net", orgpassword="asdfjklö")
        organizer2 = _get_organizer(orgemail="t@p.net", orgpassword="asdfjklö")
        db.session.add(organizer1)
        db.session.add(organizer2)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        category1 = _get_category()
        category2 = _get_category()
        db.session.add(category1)
        db.session.add(category2)
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_category(app):
    """ Test column values and restrictions of Category model """

    with app.app_context():

        category = _get_category()

        # Check for NOT NULL
        category.name = None
        db.session.add(category)
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_city(app):
    """
    Test column values and restrictions of City model
    """

    with app.app_context():
        city = _get_city()

        # Check for NOT NULL
        city.name = None
        db.session.add(city)
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_organizer(app):
    """ Test column values and restrictions of Organizer model """

    with app.app_context():
        organizer = _get_organizer()

        # Check NOT NULLs
        organizer.email = None
        db.session.add(organizer)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        organizer = _get_organizer()
        organizer.password = None
        db.session.add(organizer)
        with pytest.raises(IntegrityError):
            db.session.commit()
        
        db.session.rollback()

        # Check that Organizer name is nullable
        organizer = _get_organizer(orgname=None)
        db.session.add(organizer)
        db.session.commit()
        assert organizer.name is None

def test_venue(app):
    """
    Test Venue model attribute restrictions
    """

    with app.app_context():

        # Check for NOT Null
        city = _get_city()
        venue = _get_venue(venuecity=city)
        venue.name = None
        db.session.add(venue)
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Check for nullable
        venue.name = "Tuba"
        venue.url = None
        db.session.commit()
        assert venue.url is None

def test_event(app):
    """ Test model Event for column attribute restrictions """

    with app.app_context():
        
        # Test for NOT NULL attributes
        event = _get_event()
        db.session.add(event)
        db.session.commit()

        event.name = None
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        event.name = "Tapahtuman nimi"
        event.startTime = None
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        # Test for nullable attributes 
        event = _get_event()
        event.description = None
        db.session.add(event)
        db.session.commit()
        assert event.description is None

        # Test for foreign keys that are not nullable: Venue, Organizer, Category
        event.category = None
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        event.category = _get_category(categoryname="Jumppa")
        event.organizer = None
        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()

        event.organizer = _get_organizer(orgemail="j@p.net")
        event.venue = None
        with pytest.raises(IntegrityError):
            db.session.commit()

def test_updates(app):
    """ Test attribute updates """

    with app.app_context():

        # Create event with related objects
        city = _get_city()
        category = _get_category()
        organizer = _get_organizer()
        venue = _get_venue(venuecity=city)
        event = _get_event(evenue=venue, ecategory=category, eorganizer=organizer)
        db.session.add(event)
        db.session.commit()

        # Test that updatable attributes can be updated
        city.name = "Pori"
        category.name = "konferenssi"
        organizer.email = "jussi@pussi.net"
        organizer.password = "jjjj"
        organizer.name = "jussi"
        venue.name = "lava"
        venue.url = "oulu.fi"
        db.session.commit()
        assert city.name == "Pori"
        assert category.name == "konferenssi"
        assert organizer.email == "jussi@pussi.net"
        assert organizer.password == "jjjj"
        assert organizer.name == "jussi"
        assert venue.name == "lava"
        assert venue.url == "oulu.fi"

        # Test that foreign keys can be updated
        event.city = _get_city(cityname="Helsinki")
        event.venue = _get_venue(venuecity=event.city)
        event.category = _get_category(categoryname="Porkkanansyönti")
        event.organizer = _get_organizer(orgemail="norppa@saimaa.net")
        db.session.commit()

