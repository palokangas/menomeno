MIMETYPE = "application/vnd.collection+json"
LINK_RELATIONS_URL = ""
STORAGE_PROFILE = ""
COLLECTION_JSON_VERSION = "1.0"


class CollectionBuilder(dict):
    """
    A class for managing dictionaries that represent Collection+JSON objects.
    It provides general shorthands for managing such objects.
    """

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

        try:
            if "template" not in self["collection"]:
                self["collection"]["template"] = {"data": []}

            print("here")
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


class MenoBuilder(CollectionBuilder):
    """
    A class for creating collection+json objects for events
    and related information
    """
    pass
