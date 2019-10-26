import json
from flask import request, Response, url_for
from flask_restful import Resource
from menomeno.models import Venue, City
from menomeno.utils import get_value_for, CollectionBuilder, create_error_response, MIMETYPE
from menomeno.urls import CITY_COLLECTION_URL, CITY_URL, VENUE_COLLECTION_URL, VENUE_URL, PROFILE_URL
from menomeno import db

class VenueCollection(Resource):
    """
    Class that returns a Response object with collection of all venues in a city

    VenueCollection responds to GET and POST requests

    """

    def get(self, cityhandle):
        """
        Creates a response object for GET requests, exposing
        venues of a given city.
        
        :param str cityhandle: name of the city
        """

        print(request.headers)

        city_item = City.query.filter_by(name=cityhandle).first()
        if city_item is None:
            return create_error_response(404, "City not found",
                                "The API can not find the City requested.")

        col = CollectionBuilder()
        col_links = []
        col_links.append(col.create_link("profile", PROFILE_URL, "Link to profile"))
        col_links.append(col.create_link("up",
                                          url_for("api.cityitem", cityhandle=city_item.name),
                                          "City"))

        col.create_collection(url_for("api.venuecollection", cityhandle=city_item.name), col_links)

        print(type(Venue))
        venues = Venue.query.filter_by(city_id=city_item.id)

        for venue_item in venues:
            venuedata = []
            venuedata.append(col.create_data("name",
                                       venue_item.name,
                                       prompt="Venue name"))

            venuedata.append(col.create_data("url",
                                       venue_item.url,
                                       prompt="Venue URL"))

            venuelinks = []
            venuelinks.append(col.create_link("events-in",
                                        url_for("api.venueevents", cityhandle=city_item.name, venue_handle=venue_item.name),
                                        "Events in City"))

            col.add_item(url_for("api.venueitem", cityhandle = city_item.name, venue_handle=venue_item.name),
                                 venuedata,
                                 venuelinks)

        col.add_template_data(col.create_data("name", "", "Name of the Venue"))
        col.add_template_data(col.create_data("url", "", "URI of the Venue"))

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def post(self, cityhandle):
        """
        Adds a new venue to database. In real life, this requires admin token,
        which is not implemented here. Reads json information from request
        object: venuename and venueurl

        : param str cityhandle: name of the city to add venue in
        """

        city_item = City.query.filter_by(name=cityhandle).first()
        if city_item is None:
            return create_error_response(404, "City not found",
                                "The API can not find the City requested.")

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            req = request.json
            venuename = get_value_for('name', req)
            venueurl = get_value_for('url', req)

            if Venue.query.filter_by(name=venuename, city_id=city_item.id).first() is not None:
                return create_error_response(409, "Venue already exists",
                                             "The venue with the given name already exists is this city.")

        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        new_venue = Venue()
        new_venue.name = venuename
        new_venue.url = venueurl
        new_venue.city_id = city_item.id
        try:
            db.session.add(new_venue)
            db.session.commit()
            resp = Response(status=201)
            resp.headers['Location']= url_for('api.venueitem', cityhandle=city_item.name, venue_handle=new_venue.name)
            resp.headers['Access-Control-Expose-Headers'] = 'Location'
            return resp
        except Exception as e:
            print(e)
            print("New venue cannot be added to database. Rolling back.")
            db.session.rollback()


class VenueItem(Resource):
    """
    Class representing single venue resource. GET and PUT are supported methods.
    """

    def get(self, cityhandle, venue_handle):
        """
        Creates a response object for GET requests and error responses
        for failed requests.

        : param str cityhandle: name of the city
        : param str venue_handle: name of the venue
        """

        city_item = City.query.filter_by(name=cityhandle).first()
        if city_item is None:
            return create_error_response(404, "City not found",
                                "The API can not find the City requested.")

        col = CollectionBuilder()

        col_links = []
        col_links.append(col.create_link("profile", PROFILE_URL, "Link to profile"))
        col_links.append(col.create_link("up", url_for("api.venuecollection", cityhandle=city_item.name), "City"))

        col.create_collection(url_for("api.venuecollection", cityhandle=city_item.name), col_links)

        venue_item = Venue.query.filter_by(name=venue_handle, city_id=city_item.id).first()
        if venue_item is None:
            return create_error_response(404, "Venue not found",
                                         "The API can not find the Venue with the given name in this city.")

        venuedata = []
        venuedata.append(col.create_data("name",
                                    venue_item.name,
                                    prompt="Venue name"))

        venuedata.append(col.create_data("url",
                                    venue_item.url,
                                    prompt="Venue URL"))

        venuelinks = []
        venuelinks.append(col.create_link("events-in",
                                    url_for("api.venueevents", cityhandle=city_item.name, venue_handle=venue_item.name),
                                    "Events on this venue"))

        col.add_item(url_for("api.venueitem", cityhandle = city_item.name, venue_handle=venue_item.name),
                                venuedata,
                                venuelinks)

        col.add_template_data(col.create_data("name", venue_item.name, "Name of the Venue"))
        col.add_template_data(col.create_data("url", venue_item.url, "URI of the Venue"))

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def put(self, cityhandle, venue_handle):
        """
        Function for editing venue information. Gets values from Request:
        venue name and venue url.
        returns 204 with location header for successful edit and
        error messages for failed edits.

        : param str cityhandle: name of the city
        : param str venue_handle: name of the venue
        """

        city_item = City.query.filter_by(name=cityhandle).first()
        if city_item is None:
            return create_error_response(404, "City not found",
                                "The API can not find the City requested.")

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            req = request.json
            new_name = get_value_for('name', req)
            new_url = get_value_for('url', req)

            venue_with_same_name = Venue.query.filter_by(name=new_name, city_id=city_item.id).first()
            oldvenue = Venue.query.filter_by(name=venue_handle, city_id=city_item.id).first()
            if venue_with_same_name is not None and venue_with_same_name is not oldvenue:
                return create_error_response(409, "Venue name exists",
                                             "Trying to assign venue a name that is already a name of another venue in the same city.")
            if oldvenue is None:
                return create_error_response(404, "Venue does not exist",
                                             "The API can not find the Venue in the City requested.")

        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        try:
            oldvenue.name = new_name
            oldvenue.url = new_url
            db.session.commit()
            resp = Response(status=204)
            resp.headers['Location']= url_for('api.venueitem', cityhandle=city_item.name, venue_handle=oldvenue.name)
            resp.headers['Access-Control-Expose-Headers'] = 'Location'
            return resp
        except Exception as e:
            print(e)
            print("New venue cannot be added to database. Rolling back.")
            db.session.rollback()
