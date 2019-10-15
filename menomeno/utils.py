import json
from flask import request, Response
MIMETYPE = "application/vnd.collection+json"
LINK_RELATIONS_URL = ""
STORAGE_PROFILE = ""
COLLECTION_JSON_VERSION = "1.0"

# CollectionBuilder is based on code in the course material
# just adapted to work with collection+json

class CollectionBuilder(dict):
    """
    A class for managing dictionaries that represent Collection+JSON objects.
    It provides general shorthands for managing such objects.
    """

    @staticmethod
    def create_link(rel, href, prompt):
        """
        : param str rel: name of the link relation item
        : param str value: uri of the link item item
        : param str prompt: description of the link item
        """

        return {'rel': rel, 'href': href, 'prompt': prompt}

    @staticmethod
    def create_data(name, value, prompt):
        """
        Method for creating valid json object

        : param str name: name of the data item
        : param str value: value of the data item
        : param str promp: description of the data item

        """

        return {'name': name, 'value': value, 'prompt': prompt}

    def create_collection(self, href, links=None):
        """
        Create Collection+JSON default structure

        : param str href: hyperlink of the collection
        : param list links: list of links
        """

        self["collection"] = {}
        self["collection"]["version"] = COLLECTION_JSON_VERSION
        self["collection"]["href"] = href
        if links:
            self["collection"]["links"] = links

    def add_key(self, key, init_as_list=False, parent="collection"):
        """
        Generic function for adding keys to a parent. This could
        be implemented quite easily in code with just normal JSON
        but to standardize things it is more convenient.

        : param str key: key to add
        : param str parent: parent of the key, defaults to "collection"

        """

        try:
            if key not in self[parent]:
                if init_as_list is True:
                    self[parent][key] = []
                else:
                    self[parent][key] = {}

        except KeyError:
            print(f"Error: parent item {parent} does not exist.")

    def add_item(self, href, data, links):
        """
        Generic function to add items to a collection

        : param str href: URI of the item
        : param list data: list of dictionary objects
        : param list links: list of link objects
        """

        try:
            if "items" not in self["collection"]:
                self["collection"]["items"] = []

            newitem = {"href": href,
                       "data": data,
                       "links": links}
            self["collection"]["items"].append(newitem)

        except KeyError:
            print("KeyError. Did you forget to create the collection?")

    def add_template_data(self, data):
        """
        Function for adding data objects inside collection+json
        data array.
        """
        try:
            if "template" not in self["collection"]:
                self["collection"]["template"] = {"data": []}

            self["collection"]["template"]["data"].append(data)

        except KeyError:
            print("KeyError. Did you forget to create the collection?")

    def create_error(self, title, message):
        """
        Adds error message to object

        : param str title: Short error title
        : param str message: Longer description of error
        """

        try:
            self["collection"]["error"] = {
                "title": title,
                "message": message
            }
        except KeyError:
            print("KeyError. Did you forget to create the collection?")

def create_error_response(status_code, title, message=None):
    """
    Function for creating a descriptive error response
    """
    resource_url = request.path
    body = CollectionBuilder()
    body.create_collection(resource_url)
    body.create_error(title, message)
    return Response(json.dumps(body), status_code, mimetype=MIMETYPE)

def get_value_for(json_field, template_object):
    """
    Helper function for accessing values in collection+json data objects.
    """
    try:
        json_list = template_object['template']['data']
        target = next(item for item in json_list if item['name'] == json_field)
        return target['value']
    except KeyError:
        raise KeyError

# I ended up not using this.
class MenoBuilder(CollectionBuilder):
    """
    A class for creating collection+json objects for events
    and related information
    """
    pass
