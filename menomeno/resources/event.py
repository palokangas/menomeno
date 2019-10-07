import json
from flask import request, Response, url_for
from flask_restful import Resource
from menomeno.models import Venue, City, Event
from menomeno.utils import CollectionBuilder, create_error_response, MIMETYPE
from menomeno import db
from menomeno.urls import CITY_COLLECTION_URL, CITY_URL, VENUE_COLLECTION_URL, VENUE_URL, PROFILE_URL


class EventCollection(Resource):
    pass

class EventItem(Resource):
    pass

class VenueEvents(EventCollection):
    pass

