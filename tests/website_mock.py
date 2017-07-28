
import commentjson

_START_PAGE_KEY = 'start'
_PAGE_ID_KEY = 'page_id'
_ELEMENTS_KEY = 'elements'
_HREF_KEY = 'href'

class SchemaException(Exception):
    def __init__(self, cause):
        msg = 'Failed to parse schema, caused by ' + repr(cause)
        super(SchemaException, self).__init__(msg)
        self.cause = cause

class WebsiteDefinition():
    @staticmethod
    def verify_hrefs_exist(pages, start_page_id):
        ''' Recurses through all pages and asserts that if any element has a href
        to another page id then that page id exists
        '''
        start_page = pages[start_page_id]
        if _ELEMENTS_KEY in start_page:
            for element in start_page[_ELEMENTS_KEY]:
                if _HREF_KEY in element:
                    target_id = element[_HREF_KEY]
                    targets = [el for el in pages.values() if el[_PAGE_ID_KEY] == target_id]
                    assert (len(targets) == 1)
                    WebsiteDefinition.verify_hrefs_exist(pages, target_id)

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
            raise SchemaException(e)


class WebsiteMock():
    @classmethod
    def fromfile(json_filename):
        with open(json_filename) as file:
            js = commentjson.load(file)
            return WebsiteMock.fromjson(js)

    @classmethod
    def fromjson(json_object):
        definition = WebsiteDefinition(json_object)
        return WebsiteMock(definition)

    def init(self, definition):
        self.definition = definition
        self.current_page = self.definition.get_page(self.definition.start_page_id)
