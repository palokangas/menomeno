import os
import click
from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Based on course material
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_folder="static")
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path, "development.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    print(f"Flask app instance path set to {app.instance_path}")

    # Course material and https://flask.palletsprojects.com/en/1.0.x/tutorial/database/
    db.init_app(app)
    from . import models
    app.cli.add_command(models.init_db_command)

    from . import populate_db
    app.cli.add_command(populate_db.populate)

    from . import api
    app.register_blueprint(api.api_bp)
    
    @app.route("/cities/")
    def cities_site():
        return app.send_static_file("html/collection.html")

    @app.route("/events/")
    def events_site():
        return app.send_static_file("html/collection.html")

    @app.route("/cities/<cityhandle>/venues/")
    def venues_site(cityhandle):
        return app.send_static_file("html/collection.html")

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                            'favicon.ico',mimetype='image/vnd.microsoft.icon')
    
    print("App initialization complete. Returning app.")

    return app

