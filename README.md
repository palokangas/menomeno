# PWP SUMMER 2019
# MENONENO - Event calendar API
# Group information
* Teemu Palokangas: tpalokan at student dot oulu dot fi


### Set environment variables

    export FLASK_APP=menomeno
    export FLASK_ENV=development

### Install project

    # From top level folder

    pip install -e .

### Ipython

To work with ipython, need to push an application context. See https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/:

    from menomeno import create_app
    app = create_app()
    app.app_context().push()
    from menomeno.models import *

### Disclaimer

Flask application code structure and examples modeled after the [Flask tutorial](https://flask.palletsprojects.com/en/1.0.x/tutorial/) and its derivative [PWP Course material](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-summer-2019/). All other borrowed code is cleary indicated in code comments.
