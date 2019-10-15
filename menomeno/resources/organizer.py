import json
from flask import request, Response, url_for
from flask_restful import Resource
from menomeno.models import Organizer
from menomeno.utils import get_value_for, CollectionBuilder, create_error_response, MIMETYPE
from menomeno.urls import PROFILE_URL
from menomeno import db


class OrganizerItem(Resource):
    """
    Class representing single organizer resource. GET and PUT are supported methods.
    """

    def get(self, organizer_handle):
        """
        Creates a response object for GET requests and error 
        responses for failed attempts.

        : param str organizer_handle: organizer name
        """

        organizer_item = Organizer.query.filter_by(name=organizer_handle).first()
        if organizer_item is None:
            return create_error_response(404, "Organizer not found",
                                         "The API can not find the Organizer with the given identifier.")

        col = CollectionBuilder()
        col_links = []
        col_links.append(col.create_link("profile", PROFILE_URL, "Link to profile"))
        col.create_collection(url_for("api.organizeritem", organizer_handle=organizer_item.name), col_links)

        organizerdata = []
        organizerdata.append(col.create_data("name", organizer_item.name, "Organizer name"))
        organizerdata.append(col.create_data("email", organizer_item.email, "Organizer email"))

        organizerlinks = []
        organizerlinks.append(col.create_link("events-by", url_for("api.organizerevents",
                                                               organizer_handle=organizer_item.name),
                                                               "Events by this organizer"))

        col.add_item(url_for("api.organizeritem", organizer_handle=organizer_item.name), organizerdata, organizerlinks)

        col.add_template_data(col.create_data("name", organizer_item.name, "Organizer name"))
        col.add_template_data(col.create_data("email", organizer_item.email, "Organizer email"))
        col.add_template_data(col.create_data("password", "", "Organizer password"))

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def put(self, organizer_handle):
        """
        Function for editing organizer information. Gets values from Request:
        organizer name, email and password.
        
        Returns 204 with location header for successful edit and
        error responses for failed edits.

        : param str organizer_handle: organizer name
        """

        organizer_item = Organizer.query.filter_by(name=organizer_handle).first()
        if organizer_item is None:
            return create_error_response(404, "Organizer not found",
                                "The API can not find the Organizer requested.")

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            req = request.json
            new_name = get_value_for('name', req)
            new_email = get_value_for('email', req)
            new_password = get_value_for('password', req)
            oldorg = Organizer.query.filter_by(email=new_email).all()
            if len(oldorg) > 0:
                if len(oldorg) > 1 or oldorg[0] is not organizer_item:
                    return create_error_response(409, "Organizer email reserved",
                                                "Proposed new email already taken by another user.")


        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        try:
            organizer_item.name = new_name
            organizer_item.email = new_email
            organizer_item.password = new_password
            db.session.commit()
            resp = Response(status=204)
            resp.headers['location'] = url_for('api.organizeritem', organizer_handle=organizer_item.name)
            return resp
        except Exception as e:
            print(e)
            print("Organizer information cannot be updated in database. Rolling back.")
            db.session.rollback()
