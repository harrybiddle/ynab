
_START_PAGE_KEY = 'start'
_PAGE_ID_KEY = 'page_id'
_ELEMENTS_KEY = 'elements'

class SchemaException(Exception):
    pass

class WebsiteDefinition():
    @staticmethod
    def verify_hrefs_exist(pages, start_page_id):
        ''' Recurses through all pages and asserts that if any element has a href
        to another page id then that page id exists
        '''
        start_page = pages[start_page_id]
        if _ELEMENTS_KEY in start_page:
            for element in start_pages[_ELEMENTS_KEY]:
                if _HREF_KEY in element:
                    target_id = element[_HREF_KEY]
                    targets = [el for el in pages if el[_PAGE_ID_KEY] == target_id]
                    assert (len(targets) == 1)
                    verify_hrefs_exist(pages, target_id)

    @staticmethod
    def get_unique_pages(js):
        ''' Get all valid pages from the JSON object: i.e. dicts that have a page ID
        Asserts that no two pages share the same page ID
        '''
        pages = [el for el in js if _PAGE_ID_KEY in el]
        pages_dict = dict([(el[_PAGE_ID_KEY], el) for el in pages])
        assert (len(pages) == len(pages_dict))
        return pages_dict

    @staticmethod
    def get_unique_start_page_id(pages):
        ''' In a list of pages, find the starting page and return its page id.
        Asserts that there is exactly one starting page.
        '''
        start_pages = [el for el in pages if _START_PAGE_KEY in el]
        assert (len(start_pages) == 1)
        return start_pages[0][_PAGE_ID_KEY]

    def get_page(self, page_id):
        return self.pages[page_id]

    def __init__(self, json_object):
        try:
            self.pages = WebsiteDefinition.get_unique_pages(json_object)
            self.start_page = WebsiteDefinition.get_unique_start_page_id(self.pages.values())
            WebsiteDefinition.verify_hrefs_exist(self.pages, self.start_page)
        except Exception as e:
            raise SchemaException()


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
