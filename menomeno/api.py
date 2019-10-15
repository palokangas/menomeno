from flask import Blueprint, Response
from flask_restful import Api
from menomeno.resources import city, venue, event, organizer
from menomeno.urls import (
    CITY_COLLECTION_URL,
    CITY_URL,
    VENUE_COLLECTION_URL,
    VENUE_URL,
    VENUE_EVENTS_URL,
    ORGANIZER_URL,
    ORGANIZER_EVENTS_URL,
    EVENT_COLLECTION_URL,
    EVENT_URL
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

api.add_resource(city.CityCollection, CITY_COLLECTION_URL)
api.add_resource(city.CityItem, CITY_URL)
api.add_resource(venue.VenueCollection, VENUE_COLLECTION_URL)
api.add_resource(venue.VenueItem, VENUE_URL)
api.add_resource(event.VenueEvents, VENUE_EVENTS_URL)
api.add_resource(event.EventCollection, EVENT_COLLECTION_URL)
api.add_resource(event.EventItem, EVENT_URL)
api.add_resource(event.OrganizerEvents, ORGANIZER_EVENTS_URL)
api.add_resource(organizer.OrganizerItem, ORGANIZER_URL)


@api_bp.route('/')
def entry():
    return Response("This is the API entry point. This would be a good" \
    " place to have documentation or hypermedia for api users (but it does not)." \
    "\n But you can always try pointing your focus on <a" \
    " href=\"/api/cities\">cities</a> for starters.")

import os
from flask import send_from_directory
