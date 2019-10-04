from flask import Blueprint, Response, url_for, request, redirect
from flask_restful import Api
from menomeno.utils import CollectionBuilder
from menomeno.resources import city
from menomeno.urls import (
    CITY_COLLECTION_URL,
    CITY_URL,
    #PROFILE_URL
)

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

api.add_resource(city.CityCollection, CITY_COLLECTION_URL)
api.add_resource(city.City, CITY_URL)

@api_bp.route('/')
def entry():
    return Response("This is the API entry point. This would be a good" \
    " place to have documentation or hypermedia for api users." \
    "\n But you can always try pointing your focus on <a" \
    " href=\"/api/cities\">cities</a> for starters.")

