
class WebsiteMock():
    @classmethod
    def fromfile(json_filename):
        with open(json_filename) as file:
            js = json.load(file)
            return WebsiteMock(js)

    @staticmethod
    def verify_schema(json_object):
        raise ValueError()

    def init(self, json_object):
        WebsiteMock.verify_schema(json_object)
        self._contents = json_object
        self.current_page = json_object['starting_page']
