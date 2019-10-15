# PWP SUMMER 2019
# MENONENO - Event calendar API
# Group information
* Teemu Palokangas: tpalokan at student dot oulu dot fi


## To set up environment

### Create virtual environment

For example in python3-venv:

    python3 -m venv menomeno

Then

    source path-to-menomeno/bin/activate

### Set environment variables

    export FLASK_APP=menomeno
    export FLASK_ENV=development
    
    or using the script

    source set_env.sh
    
### Python version, dependencies and installation of the project

The project is using Python version 3.6.8. The rest of the dependencies can be installed inside a virtual environment with:

    pip install -r requirements.txt

To install the project

    pip install -e .

To initialize database and populate it with test data

    flask init-db
    flask populate-models

To run test, either:

    # To run tests
    pytest

    # To run tests with coverage information
    ./testcov.sh

### Ipython

To work with ipython, need to push an application context. See https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/:

    from menomeno import create_app
    app = create_app()
    app.app_context().push()
    from menomeno.models import *

### Disclaimer

Flask application code structure and examples modeled after the [Flask tutorial](https://flask.palletsprojects.com/en/1.0.x/tutorial/) and its derivative [PWP Course material](https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-summer-2019/). All other borrowed code is cleary indicated in code comments.

The local Javascript & JQuery client is a generalized adaptation of one provided in course material.
