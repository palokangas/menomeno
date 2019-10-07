import json
from flask import request, Response, url_for
from flask_restful import Resource
from menomeno.models import City
from menomeno.utils import CollectionBuilder, create_error_response, MIMETYPE
from menomeno.urls import CITY_COLLECTION_URL, PROFILE_URL
from menomeno import db


class CityCollection(Resource):
    """
    Class that returns a Response object with collection of all cities
    Ideally there would be different collection for cities
    such as cities in one country or other region...

    CityCollection responds to GET and POST requests

    """

    def get(self):
        """ Creates a response object for GET requests"""

        col = CollectionBuilder()
        col_links = col.create_link("profile", PROFILE_URL, "Link to profile")
        col.create_collection(CITY_COLLECTION_URL, col_links)

        cities = City.query.all()

        for city_item in cities:
            citydata = col.create_data("name",
                                       city_item.name,
                                       prompt="City name")
            citylinks = col.create_link("venues-in",
                                        (url_for("api.venue.venuecollection", cityhandle = city_item.name.lower())),
                                        "Venues in City")

            col.add_item(url_for("api.citycollection"),
                                 [citydata],
                                 [citylinks])

        templatedata = col.create_data("name", "", "Name of the City")
        col.add_template_data(templatedata)

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)

    def post(self):
        """
        Adds a new city to database. In real life, this requires admin token,
        which is not implemented here. Reads json information from request
        object.
        """

        if request.method != "POST":
            return "POST method required", 405
        else:
            print("POSTing product information")

        col = CollectionBuilder()
        col.create_collection(CITY_COLLECTION_URL)

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            print("Problem with json formatting: {}. \n JSON provided was: \n {json.dumps(request.json)}".format(e))
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")
        except:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            cityname = request.json['value']
            if City.query.filter_by(name=cityname).first() is not None:
                return create_error_response(409, "City already exists",
                                             "The city name given already exists")

        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        except ValueError:
            return create_error_response(400, "Invalid types",
                            "Weight and price must be numbers")

        new_city = City()
        new_city.name = cityname
        try:
            db.session.add(new_city)
            db.session.commit()
            resp = Response(status=201)
            resp.headers['location']= url_for('api.city', cityhandle=new_city.name)
            return resp
        except Exception as e:
            print(e)
            print("New city cannot be added to database. Rolling back.")
            db.session.rollback()


class CityItem(Resource):
    """
    Class representing city resource. GET and PUT are supported methods.
    """

    def get(self, cityhandle):
        """
        Creates a response object for GET requests

        : param str cityhandle: Handle, ie. name of the city
        """

        col = CollectionBuilder()
        col_links = col.create_link("profile", PROFILE_URL, "Link to profile")
        col.create_collection(CITY_COLLECTION_URL, col_links)

        city_item = City.query.filter_by(name=cityhandle).first()
        if city_item is None:
            return create_error_response(404, "City not found",
                                "The API can not find the City requested.")

        citydata = col.create_data("name",
                                    city_item.name,
                                    prompt="City name")
        citylinks = col.create_link("venues-in",
                                    (url_for("api.venuecollection", cityhandle=city_item.name)),
                                    "Venues in City")

        col.add_item(url_for("api.cityitem", cityhandle=city_item.name),
                                [citydata],
                                [citylinks])

        templatedata = col.create_data("name", "", "Name of the City")
        col.add_template_data(templatedata)

        return Response(json.dumps(col), 200, mimetype=MIMETYPE)


    def put(self, cityhandle):
        """
        Function for editing city information. Gets values from Request,
        returns 201 with location header for successful edit and
        error messages for failed edits.

        : param str cityhandle: Handle, ie. name of the city
        """

        if request.method != "PUT":
            return "PUT method required", 405
        else:
            print("Editing product information")

        col = CollectionBuilder()
        col.create_collection(CITY_COLLECTION_URL)

        try:
            json.loads(str(request.json).replace("\'", "\""))
        except (TypeError, ValueError) as e:
            print("Problem with json formatting: {}. \n JSON provided was: \n {json.dumps(request.json)}".format(e))
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")
        except:
            return create_error_response(415, "Not JSON",
                             "Request content type must be JSON")

        try:
            cityname = request.json['value']
            city_with_same_name = City.query.filter_by(name=cityname).first()
            oldcity = City.query.filter_by(name=cityhandle).first()
            if city_with_same_name is not None and city_with_same_name is not oldcity:
                return create_error_response(409, "City name exists",
                                             "Trying to assign city a name that is already a name of another city.")
            if oldcity is None:
                return create_error_response(404, "City does not exist",
                                             "The API can not find the City requested.")

        except KeyError:
            return create_error_response(400, "Incomplete request",
                            "Incomplete request - missing fields")

        except ValueError:
            return create_error_response(400, "Invalid types",
                            "Weight and price must be numbers")

        try:
            oldcity.name = cityname
            db.session.commit()
            resp = Response(status=201)
            resp.headers['location']= url_for('api.city', cityhandle=cityname)
            return resp
        except Exception as e:
            print(e)
            print("New city cannot be added to database. Rolling back.")
            db.session.rollback()
