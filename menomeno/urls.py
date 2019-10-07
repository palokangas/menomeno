"""
Urls of the API collected to a single point
"""

CITY_COLLECTION_URL = "/cities/"
CITY_URL = "/cities/<cityhandle>/"
VENUE_COLLECTION_URL = "/cities/<cityhandle>/venues/"
VENUE_URL = "/cities/<cityhandle>/venues/<venue_handle>/"
VENUE_EVENTS_URL = "/cities/<cityhandle>/venues/<venue_handle>/events/"
EVENT_COLLECTION_URL = "/events/"
EVENT_URL = "/events/<event_handle>/"
ORGANIZER_URL = "/organizers/<organizer_handle>/"
ORGANIZER_EVENTS_URL = "/organizers/<organizer_handle>/events/"
PROFILE_URL = "https://app.apiary.io/menomenoapi"
