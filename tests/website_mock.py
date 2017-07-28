
_START_PAGE_KEY = 'start_page'
_PAGE_ID_KEY = 'page_id'

class SchemaException(Exception):
    pass

class WebsiteDefinition():
    @staticmethod
    def verify_schema(json_object):
        try:
            start_page_elements = [el for el in json_object if _START_PAGE_KEY in el]
            assert (len(start_page_elements) == 1)
            start_page_id = start_page_elements[0][_START_PAGE_KEY]
            page_ids = [el[_PAGE_ID_KEY] for el in json_object if _PAGE_ID_KEY in el]
            page_ids_as_dict = dict([(id, None) for id in page_ids])
            assert (len(page_ids_as_dict) == len(page_ids))
            assert (start_page_id in page_ids)
        except Exception as e:
            raise SchemaException()
        return start_page_id

    def init(self, json_object):
        self.start_page, self.pages = self.verify_schema(json_object)

    def start_page(self):
        return self._contents

class WebsiteMock():
    @classmethod
    def fromfile(json_filename):
        with open(json_filename) as file:
            js = json.load(file)
            return WebsiteMock(js)



    def init(self, json_object):
        WebsiteMock.verify_schema(json_object)
        self._contents = json_object
        self.current_page = json_object[_START_PAGE_KEY]
