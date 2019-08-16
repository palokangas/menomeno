# PWP SUMMER 2019
# MENONENO - Event calendar API
# Group information
* Teemu Palokangas: tpalokan at student dot oulu dot fi


### Set environment variables

    export FLASK_APP=menomeno
    export FLASK_ENV=development

### Ipython

To work with ipython, need to push an application context. See https://flask-sqlalchemy.palletsprojects.com/en/2.x/contexts/:

    from menomeno import create_app
    app = create_app()
    app.app_context().push()
    from menomeno.models import *

