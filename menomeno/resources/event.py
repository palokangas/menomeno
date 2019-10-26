import json
from datetime import datetime
from flask import request, Response, url_for
from flask_restful import Resource
from menomeno.models import Venue, City, Event, Organizer, Category
from menomeno.utils import get_value_for, CollectionBuilder, create_error_response, MIMETYPE
from menomeno.urls import CITY_COLLECTION_URL, CITY_URL, VENUE_COLLECTION_URL, VENUE_URL, PROFILE_URL
from menomeno import db


class EventCollection(Resource):
    """
    Class that exposes Event resources, accommodates for
    subclass use by VenueEvents and OrganizerEvents

    EventCollection responds to GET and POST requests

    """

    def get(self, cityhandle=None, venue_handle=None, organizer_handle=None):
        """
        Creates a response object for GET requests

        :param str cityhandle: city name
        :param str venue_handle: venue name
        :param str organizer_handle: organizer name
        """

        # Initialize things in case Events for Venue are requested
        if cityhandle and venue_handle:

            city_item = City.query.filter_by(name=cityhandle).first()
            if city_item is None:
                return create_error_response(404, "City not found",
                                    "The API can not find the City requested.")

            venue_item = Venue.query.filter_by(name=venue_handle, city_id=city_item.id).first()
            if venue_item is None:
                return create_error_response(404, "Venue not found",
                                             "The API can not find the Venue in this City.")

            collection_url = url_for("api.venueevents", venue_handle=venue_item.name, cityhandle=city_item.name)
            up = url_for("api.venueitem", venue_handle=venue_item.name, cityhandle=city_item.name)
            up_prompt = "Venue"
            events = Event.query.filter_by(venue_id = venue_item.id)

        # Initialize things in case Events for Organizer are requested
        elif organizer_handle:
            is_organizer_collection = True

            organizer_item = Organizer.query.filter_by(name=organizer_handle).first()
            if organizer_item is None:
                return create_error_response(404, "Organizer not found",
                                             "The API can not find the Organizer requested.")

            up = url_for("api.organizeritem", organizer_handle=organizer_item.name)
            collection_url = url_for("api.organizerevents", organizer_handle=organizer_item.name)
            up_prompt = "Organizer"
            events = Event.query.filter_by(organizer_id=organizer_item.id)

        # Initialize things if general Event collection is requested
        else:
            up = url_for("api.eventcollection")
            up_prompt = "All events"
            collection_url = url_for("api.eventcollection")
            events = Event.query.all()


        col = CollectionBuilder()
        col_links = []
        col_links.append(col.create_link("profile", PROFILE_URL, "Link to profile"))
        col_links.append(col.create_link("up", up, up_prompt))

        col.create_collection(collection_url, col_links)

        for event_item in events:
            eventdata = []
            eventdata.append(col.create_data("name", event_item.name, "Event name"))
            eventdata.append(col.create_data("description", event_item.description, "Event description"))
            eventdata.append(col.create_data("organizer", event_item.organizer.name, "Organizer of the Event"))
            eventdata.append(col.create_data("venue", event_item.venue.name, "Venue of the Event"))
            eventdata.append(col.create_data("venue_url", event_item.venue.url, "Venue URL"))
            eventdata.append(col.create_data("startTime", event_item.startTime.isoformat(), "Start time of the Event"))
            eventdata.append(col.create_data("category", event_item.category.name, "Category of the Event"))

            eventlinks = []
            eventlinks.append(col.create_link("up", up, up_prompt))

            col.add_item(url_for("api.eventitem", event_handle=event_item.url), eventdata, eventlinks)

        col.add_template_data(col.create_data("name", "", "Event name"))
        col.add_template_data(col.create_data("description", "", "Event description"))
        col.add_template_data(col.create_data("startTime", "", "Start time of the Event"))
        col.add_template_data(col.create_data("organizer", "", "Organizer of the Event"))
        col.add_template_data(col.create_data("venue", "", "Venue of the Event"))
        col.add_template_data(col.create_data("city", "", "City of the Event"))

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def post(self):
        """
        Adds a new event to database. Reads json information from request
        object: name, description, venue, city, organizer and startTime
        """

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            req = request.json
            eventname = get_value_for('name', req)
            eventdesc = get_value_for('description', req)
            venuename = get_value_for('venue', req)
            cityname = get_value_for('city', req)
            organizername = get_value_for('organizer', req)
            starttime_string = get_value_for('startTime', req)

            try:
                starttime = datetime.strptime(starttime_string, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                return create_error_response(400, "Wrong time format",
                                "Time was passed in wrong format")

            # Category is not implemented. Using just on category for all
            category = Category.query.first()
            if category is None:
                return create_error_response(404, "Category not found",
                                             "Client is trying to add an event to Category that does not exist.")

            city = City.query.filter_by(name=cityname).first()
            venue = Venue.query.filter_by(name=venuename, city_id=city.id).first()
            if venue is None:
                return create_error_response(404, "City or Venue not found",
                                             "Client is trying to add an event to City or Venue that cannot be found.")

            organizer = Organizer.query.filter_by(name=organizername).first()
            if organizer is None:
                return create_error_response(404, "Organizer not found",
                                             "Client is trying to add Event to organizer that cannot be found.")


        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        newevent = Event()
        newevent.name = eventname
        newevent.description = eventdesc
        newevent.startTime = starttime
        newevent.venue = venue
        newevent.organizer = organizer
        newevent.category = category

        newevent.set_url()

        if Event.query.filter_by(url=newevent.url).first() is not None:
                return create_error_response(409, "Event already exist",
                                             "Event with same name, venue and time already exists.") 

        try:
            db.session.add(newevent)
            db.session.commit()
            resp=Response(status=201)
            resp.headers['Location']=url_for('api.eventitem', event_handle=newevent.url)
            resp.headers['Access-Control-Expose-Headers'] = 'Location'
            return resp
        except:
            print("Commit failed. Rolling back.")
            db.session.rollback()


class EventItem(Resource):
    """
    Class representing single event resource. GET, PUT and DELETE are supported methods.
    """

    def get(self, event_handle):
        """
        Creates a response object for GET requests

        : param str event_handle: URI base of the event (autoformatted from name, venue and time)
        """

        event_item = Event.query.filter_by(url=event_handle).first()
        if event_item is None:
            return create_error_response(404, "Event not found",
                                         "The API can not find the Event with the given identifier.")

        col = CollectionBuilder()
        col_links = []
        col_links.append(col.create_link("profile", PROFILE_URL, "Link to profile"))
        col.create_collection(url_for("api.eventcollection"), col_links)

        eventdata = []
        eventdata.append(col.create_data("name", event_item.name, "Event name"))
        eventdata.append(col.create_data("description", event_item.description, "Event description"))
        eventdata.append(col.create_data("organizer", event_item.organizer.name, "Organizer of the Event"))
        eventdata.append(col.create_data("venue", event_item.venue.name, "Venue of the Event"))
        eventdata.append(col.create_data("venue_url", event_item.venue.url, "Venue URL"))
        eventdata.append(col.create_data("startTime", event_item.startTime.isoformat(), "Start time of the Event"))
        eventdata.append(col.create_data("category", event_item.category.name, "Category of the Event"))

        eventlinks = []
        eventlinks.append(col.create_link("collection", url_for("api.eventcollection"), "All events"))
        eventlinks.append(col.create_link("in-venue", url_for("api.venueitem",
                                                              venue_handle=event_item.venue.name,
                                                              cityhandle=event_item.venue.city.name),
                                                              "Venue"))
        eventlinks.append(col.create_link("organized-by", url_for("api.organizerevents",
                                                                  organizer_handle=event_item.organizer.name),
                                                                  "Organizer's other events"))
        # eventlinks.append(col.create_link("in-city", up, up_prompt))
        # eventlinks.append(col.create_link("in-category", up, up_prompt))
        # City-based Events and Categories not implemented yet

        col.add_item(url_for("api.eventitem", event_handle=event_item.url), eventdata, eventlinks)

        col.add_template_data(col.create_data("name", event_item.name, "Event name"))
        col.add_template_data(col.create_data("description", event_item.description, "Event description"))
        col.add_template_data(col.create_data("startTime", event_item.startTime.isoformat(), "Start time of the Event"))
        #col.add_template_data(col.create_data("organizer", event_item.organizer.name, "Organizer of the Event"))
        #col.add_template_data(col.create_data("venue", event_item.venue.name, "Venue of the Event"))
        #col.add_template_data(col.create_data("city", event_item.venue.city.name, "City of the Event"))
 
        print(col)
        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def put(self, event_handle):
        """
        Function for editing event information. Gets values from Request:
        name, description, startTime, organizer, venue and city.
        Returns 204 with location header for successful edit and
        error responses for failed edits.

        : param str event_handle: url base of the venue
        """

        event_item = Event.query.filter_by(url=event_handle).first()
        if event_item is None:
            return create_error_response(404, "Event not found",
                                "The API can not find the Event requested.")

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            req = request.json
            new_name = get_value_for('name', req)
            new_description = get_value_for('description', req)
            new_time = get_value_for('startTime', req)

        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")


        event_item.name = new_name
        event_item.description = new_description
        event_item.startTime = datetime.strptime(new_time, '%Y-%m-%dT%H:%M:%S')
        event_item.set_url()

        evs = Event.query.filter_by(url=event_item.url).all()
        if evs is not None:
            for e in evs:
                print(e)
            if len(evs) > 1 or evs[0] is not event_item:
                return create_error_response(409, "Event already exist",
                                             "Event with same name, venue and time already exists.") 

        try:
            db.session.commit()
            resp = Response(status=204)
            resp.headers['Location'] = url_for('api.eventitem', event_handle=event_item.url)
            resp.headers['Access-Control-Expose-Headers'] = 'Location'
            return resp
        except Exception as e:
            print(e)
            print("New event cannot be added to database. Rolling back.")
            db.session.rollback()

    def delete(self, event_handle):
        """
        Function for deleting event information. Returns 204 for
        successful delete, error responses for failed attemps.

        : param str event_handle: url base of the venue
        """

        event_item = Event.query.filter_by(url=event_handle).first()
        if event_item is None:
            return create_error_response(404, "Event not found",
                                "The API can not find the Event requested.")

        try:
            db.session.delete(event_item)
            db.session.commit()
            return Response(status=204)
        except Exception as e:
            print(e)
            print("Event cannot be deleted. Rolling back")
            db.session.rollback()
            return create_error_response(400, "Database operation failed",
                                        "Product cannot be deleted. Rolling back.")


class VenueEvents(EventCollection):
    """
    Subclass of EventCollection that uses super methods for everything.
    Implemented just to expose multiple collections of Events.
    """
    def get(self, cityhandle, venue_handle):
        return super().get(cityhandle=cityhandle, venue_handle=venue_handle)
    
    def post(self, cityhandle, venue_handle):
        return super().post()


class OrganizerEvents(EventCollection):
    """
    Subclass of EventCollection that uses super methods for everything.
    Implemented just to expose multiple collections of Events.
    """
    def get(self, organizer_handle):
        return super().get(organizer_handle=organizer_handle)

    def post(self, organizer_handle):
        return super().post()