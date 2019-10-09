# These tests based entirely on the template of the
# Programmable Web -course
import json
import os
import pytest
import tempfile
import time
from datetime import datetime
from jsonschema import validate
from sqlalchemy.engine import Engine
from sqlalchemy import event
from sqlalchemy.exc import IntegrityError, StatementError

from menomeno.populate_db import populate_models
from menomeno import create_app, db
from menomeno.models import Event, Venue, Category, City, Organizer


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# based on http://flask.pocoo.org/docs/1.0/testing/
# we don't need a client for database testing, just the db handle
@pytest.fixture
def client():
    db_fd, db_fname = tempfile.mkstemp()
    config = {}
    config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + db_fname
    config["TESTING"] = True

    app = create_app(config)

    with app.app_context():
        db.create_all()
        _populate_db()

    yield app.test_client()

    db.session.remove()
    os.close(db_fd)
    os.unlink(db_fname)

def _populate_db():

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

def _get_sensor_json(joku):
    pass

def _get_city_template(cityname):
    """
    Creates a valid JSON object to be used for PUT and POST tests.
    """

    return {"template": {"data": [{"name": "name",
                                   "value": cityname,
                                   "prompt": "Name of the City"},
                                  {"name": "url",
                                   "value": "",
                                   "prompt": "URI of the Venue"}]}}

def _get_venue_template(venuename, venueurl):
    """
    Creates a valid JSON object to be used for PUT and POST tests.
    """

    return {"template": {"data": [{"name": "name",
                                   "value": venuename,
                                   "prompt": "Name of the Venue"},
                                  {"name": "url",
                                   "value": venueurl,
                                   "prompt": "URI of the Venue"}]}}

def _check_collection_validity(client, response):
    """
    Checks for valid collection+json structure and elements: presence of versioninfo
    and checks if collection href and links work and items and links have correct
    fields present. Note: checks for structure, not content itself (except for links).
    """
    coll = response["collection"]
    assert coll["version"] is not None
    href = coll["href"]
    resp = client.get(href)
    assert resp.status_code == 200
    if coll["links"] is not None:
        for link in coll["links"]:
            linkref = link["href"]
            if linkref[0:4] == "/api":
                resp = client.get(linkref)
                assert resp.status_code == 200

    try:
        collitems = coll["items"]
    except KeyError:
        collitems = None

    # If Items present, test their structure
    if collitems:
        for item in coll["items"]:
            assert item['href'] is not None
            for data in item['data']:
                assert data['name'] is not None
                assert data['value'] is not None
                assert data['prompt'] is not None


            try:
                itemlinks = item['links']
            except KeyError:
                itemlinks = None

            if itemlinks:
                for link in item['links']:
                    assert link['rel'] is not None
                    assert link['href'] is not None
                    assert link['prompt'] is not None
                    resp = client.get(link['href'])
                    assert resp.status_code == 200
                # If template present, test its structure

    try:
        colltemplate = coll["template"]
    except KeyError:
        colltemplate = None

    if colltemplate:
        for item in coll["template"]["data"]:
            assert item['name'] is not None
            assert item['value'] is not None
            assert item['prompt'] is not None

    # If error present, test its structure
    try:
        collerror = coll["error"]
    except KeyError:
        collerror = None

    if collerror:
        error = coll["error"]
        assert error["title"] is not None
        assert error["message"] is not None


def _check_namespace(client, response):
    """
    Checks that the "senhub" namespace is found from the response body, and
    that its "name" attribute is a URL that can be accessed.
    """

    ns_href = response["@namespaces"]["senhub"]["name"]
    resp = client.get(ns_href)
    assert resp.status_code == 200

def _check_control_get_method(ctrl, client, obj):
    """
    Checks a GET type control from a JSON object be it root document or an item
    in a collection. Also checks that the URL of the control can be accessed.
    """

    href = obj["@controls"][ctrl]["href"]
    resp = client.get(href)
    assert resp.status_code == 200

def _check_control_delete_method(ctrl, client, obj):
    """
    Checks a DELETE type control from a JSON object be it root document or an
    item in a collection. Checks the contrl's method in addition to its "href".
    Also checks that using the control results in the correct status code of 204.
    """

    href = obj["@controls"][ctrl]["href"]
    method = obj["@controls"][ctrl]["method"].lower()
    assert method == "delete"
    resp = client.delete(href)
    assert resp.status_code == 204

def _check_control_put_method(ctrl, client, obj):
    """
    Checks a PUT type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 204.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "put"
    assert encoding == "json"
    body = _get_sensor_json()
    body["name"] = obj["name"]
    validate(body, schema)
    resp = client.put(href, json=body)
    assert resp.status_code == 204

def _check_control_post_method(ctrl, client, obj):
    """
    Checks a POST type control from a JSON object be it root document or an item
    in a collection. In addition to checking the "href" attribute, also checks
    that method, encoding and schema can be found from the control. Also
    validates a valid sensor against the schema of the control to ensure that
    they match. Finally checks that using the control results in the correct
    status code of 201.
    """

    ctrl_obj = obj["@controls"][ctrl]
    href = ctrl_obj["href"]
    method = ctrl_obj["method"].lower()
    encoding = ctrl_obj["encoding"].lower()
    schema = ctrl_obj["schema"]
    assert method == "post"
    assert encoding == "json"
    body = _get_sensor_json()
    validate(body, schema)
    resp = client.post(href, json=body)
    assert resp.status_code == 201

class TestEntryPoint(object):
    """
    This class tests just the static entry point
    """
    RESOURCE_URL = "/api/"

    def test_get(self, client):
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200


class TestCityCollection(object):
    """
    This class implements tests for each HTTP method in sensor collection
    resource.
    """

    RESOURCE_URL = "/api/cities/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that the collection structure is valid and test data is
        present.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_collection_validity(client, body)
        assert len(body["collection"]["items"]) == 2


    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 201 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_city_template("testcity")

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["template"]["data"][0]["value"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["collection"]["href"] == "/api/cities/"
        assert body["collection"]["items"][0]["href"] == "/api/cities/testcity/"

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # remove model field for 400
        valid["template"]["data"][0].pop("value")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestCityItem(object):

    RESOURCE_URL = "/api/cities/city1/"
    INVALID_URL = "/api/cities/shangri-la/"
    MODIFIED_URL = "/api/cities/oulu/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes are present.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_collection_validity(client, body)
        assert body["collection"]["href"] == "/api/cities/" # RESOURCE_URL
        assert body["collection"]["items"][0]["data"][0]["value"] == "city1"
        assert len(body["collection"]["items"]) == 1

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        """

        valid = _get_city_template("oulu")

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another sensor's name
        valid["template"]["data"][0]["value"] = "city2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # test with valid (only change model)
        valid["template"]["data"][0]["value"] = "oulu"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove field for 400
        valid["template"]["data"][0].pop("value")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_city_template("oulu")
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["collection"]["items"][0]["data"][0]["value"] == valid["template"]["data"][0]["value"]


class TestVenueCollection(object):
    """
    This class implements tests for each HTTP method in Venue collection
    resource.
    """

    RESOURCE_URL = "/api/cities/city1/venues/"
    WRONGCITY_URL = "/api/cities/wrongcity/venues/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that the collection structure is valid and test data is
        present.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_collection_validity(client, body)
        assert len(body["collection"]["items"]) == 2
        resp = client.get(self.WRONGCITY_URL)
        assert resp.status_code == 404

    def test_post(self, client):
        """
        Tests the POST method. Checks all of the possible error codes, and
        also checks that a valid request receives a 204 response with a
        location header that leads into the newly created resource.
        """

        valid = _get_venue_template("testvenue", "venueurl")

        # test with wrong content type
        resp = client.post(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        # test with valid and see that it exists afterward
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 201
        assert resp.headers["Location"].endswith(self.RESOURCE_URL + valid["template"]["data"][0]["value"] + "/")
        resp = client.get(resp.headers["Location"])
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["collection"]["href"] == "/api/cities/city1/venues/"
        assert body["collection"]["items"][0]["href"] == "/api/cities/city1/venues/testvenue/"

        # send same data again for 409
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # remove model field for 400
        valid["template"]["data"][0].pop("value")
        resp = client.post(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400


class TestVenueItem(object):

    RESOURCE_URL = "/api/cities/city1/venues/venuename1-1/"
    INVALID_URL = "/api/cities/city1/venues/wrongvenue/"
    MODIFIED_URL = "/api/cities/city1/venues/newvenue/"
    WRONGCITY_URL = "/api/cities/wrongcity/venues/venuename1-1/"

    def test_get(self, client):
        """
        Tests the GET method. Checks that the response status code is 200, and
        then checks that all of the expected attributes are present.
        """

        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        _check_collection_validity(client, body)
        assert body["collection"]["items"][0]["href"] == "/api/cities/city1/venues/venuename1-1/" # RESOURCE_URL
        assert len(body["collection"]["items"]) == 1

        resp = client.get(self.INVALID_URL)
        assert resp.status_code == 404

    def test_put(self, client):
        """
        Tests the PUT method. Checks all of the possible error codes, and also
        checks that a valid request receives a 204 response. Also tests that
        when name is changed, the sensor can be found from a its new URI.
        """

        valid = _get_venue_template("newvenue", "newurl")

        # test with wrong content type
        resp = client.put(self.RESOURCE_URL, data=json.dumps(valid))
        assert resp.status_code == 415

        resp = client.put(self.INVALID_URL, json=valid)
        assert resp.status_code == 404

        # test with another venue's name
        valid["template"]["data"][0]["value"] = "venuename1-2"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 409

        # TÄHÄN JÄI KESKEN
        # test with wrong city
        valid["template"]["data"][0]["value"] = "newvenue"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # test with valid (only change model)
        valid["template"]["data"][0]["value"] = "newvenue"
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 204

        # remove field for 400
        valid["template"]["data"][0].pop("value")
        resp = client.put(self.RESOURCE_URL, json=valid)
        assert resp.status_code == 400

        valid = _get_venue_template("newvenue", "newurl")
        resp = client.put(self.RESOURCE_URL, json=valid)
        resp = client.get(self.MODIFIED_URL)
        assert resp.status_code == 200
        body = json.loads(resp.data)
        assert body["collection"]["items"][0]["data"][0]["value"] == valid["template"]["data"][0]["value"]

    def _test_delete(self, client):
        """
        Tests the DELETE method. Checks that a valid request reveives 204
        response and that trying to GET the sensor afterwards results in 404.
        Also checks that trying to delete a sensor that doesn't exist results
        in 404.
        """

        resp = client.delete(self.RESOURCE_URL)
        assert resp.status_code == 204
        resp = client.get(self.RESOURCE_URL)
        assert resp.status_code == 404
        resp = client.delete(self.INVALID_URL)
        assert resp.status_code == 404


















