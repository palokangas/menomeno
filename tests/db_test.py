import os
import tempfile
import pytest

from menomeno import create_app, db
from menomeno.models import Event, Venue, Category, City, Organizer

@pytest.fixture
def app():
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

