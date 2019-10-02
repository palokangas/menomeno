from flask import Blueprint, Response, url_for, request, redirect
from flask_restful import Api

api_bp = Blueprint('api', __name__, url_prefix='/api')
#api = Api(api_bp)


@api_bp.route('/')
def entry():
    return Response("This is the API entry point. It does not have hypermedia!")

@api_bp.route('/cities/')
def cities():
    return "Cities placeholder"
