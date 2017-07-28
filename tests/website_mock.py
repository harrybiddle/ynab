
import commentjson

_START_PAGE_KEY = 'start'
_PAGE_ID_KEY = 'page_id'
_ELEMENTS_KEY = 'elements'
_HREF_KEY = 'href'
_NAME_KEY = 'name'
_ID_KEY = 'id'
_XPATH_KEY = 'xpath'

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

    @staticmethod
    def find_element_in_page(page, key, identifier):
        if _ELEMENTS_KEY in page:
            ret = []
            for element in page[_ELEMENTS_KEY]:
                if key in element and element[key] == identifier:
                    ret.append(element)
            if len(ret) == 0:
                raise KeyError(key + ': ' + identifier)
            return ret[0]
        else:
            raise KeyError('No elements in page')

    def get_page(self, page_id):
        return self.pages[page_id]

    def __init__(self, json_object):
        try:
            self.pages = WebsiteDefinition.get_unique_pages(json_object)
            self.start_page = WebsiteDefinition.get_unique_start_page_id(self.pages.values())
            WebsiteDefinition.verify_hrefs_exist(self.pages, self.start_page)
        except Exception as e:
            raise SchemaException(e)


class Element():
    def __init__(self, website, element):
        self._website = website
        self.contents = element

    def click(self):
        if _HREF_KEY in self.contents:
            target_page_id = self.contents[_HREF_KEY]
            self._website.set_current_page(target_page_id)


class WebsiteMock():
    @classmethod
    def fromfile(cls, json_filename):
        with open(json_filename) as file:
            js = commentjson.load(file)
            return cls.fromjson(js)

    @classmethod
    def fromjson(cls, json_object):
        definition = WebsiteDefinition(json_object)
        return cls(definition)

    def __init__(self, definition):
        self.definition = definition
        self._current_page = self.definition.get_page(self.definition.start_page)

    def set_current_page(self, new_page_id):
        self._current_page = self.definition.get_page(new_page_id)

    def current_page(self):
        return self._current_page[_PAGE_ID_KEY]

    def find_element_by_name(self, name):
        page = self._current_page
        element = WebsiteDefinition.find_element_in_page(page, _NAME_KEY, name)
        return Element(self, element)

    def find_element_by_xpath(self, xpath):
        page = self._current_page
        element = WebsiteDefinition.find_element_in_page(page, _XPATH_KEY, xpath)
        return Element(self, element)

    def find_element_by_id(self, id):
        page = self._current_page
        element = WebsiteDefinition.find_element_in_page(page, _ID_KEY, id)
        return Element(self, element)

    def get(self, _):
        pass

    def switch_to_default_content(self):
        pass

    def switch_to_frame(self, _):
        pass

