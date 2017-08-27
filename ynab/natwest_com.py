from selenium.webdriver.support.ui import Select

from bank import Bank

class Natwest(Bank):

    full_name = 'Natwest'

    def __init__(self, config):
        super(Natwest, self).__init__(['pin', 'password'])
        self.customer_number = config['customer number']

    def download_transactions(self, driver, _):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _go_to_website(self, driver):
        driver.get('https://www.nwolb.com')

    def _switch_to_security_frame(self, driver):
        driver.switch_to_default_content()
        driver.switch_to_frame('ctl00_secframe')

    def _log_in_customer_number(self, driver):
        self._switch_to_security_frame(driver)
        search_box = driver.find_element_by_name(
            'ctl00$mainContent$LI5TABA$DBID_edit')
        search_box.send_keys(self.customer_number)
        search_box.submit()

    def _select_characters(self, texts_requesting_pin_digits,
                           texts_requesting_password_chars):
        ''' Takes a list of phrases like "Enter the xth number" that are asking
        for a subset of the pin/password, and returns that subset.'''
        def extract_int_minus_one(unicode):
            string = unicode.encode('ascii', 'ignore')
            return int(filter(str.isdigit, string)) - 1
        pin_digits = map(extract_int_minus_one, texts_requesting_pin_digits)
        password_chars = map(extract_int_minus_one,
                             texts_requesting_password_chars)
        return (''.join(map(self.secret('pin').__getitem__, pin_digits)),
                ''.join(map(self.secret('password').__getitem__, password_chars)))

    def _log_in_pin_and_password(self, driver):
        # get the text asking for the pin digits and password chars
        texts_requesting_pin_digits = [
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALALabel').text,
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALBLabel').text,
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALCLabel').text]
        texts_requesting_password_chars = [
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALDLabel').text,
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALELabel').text,
            driver.find_element_by_id('ctl00_mainContent_Tab1_LI6DDALFLabel').text]

        # extract the requested info from the secret
        subpin, subpassword = self._select_characters(texts_requesting_pin_digits,
                                                      texts_requesting_password_chars)

        # find the text boxes on the page
        pin_text_boxes = [
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPEA_edit'),
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPEB_edit'),
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPEC_edit')]
        password_text_boxes = [
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPED_edit'),
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPEE_edit'),
            driver.find_element_by_name('ctl00$mainContent$Tab1$LI6PPEF_edit')]

        # fill the text boxes
        for digit, box in zip(subpin, pin_text_boxes):
            box.send_keys(digit)

        for char, box in zip(subpassword, password_text_boxes):
            box.send_keys(char)

        # click through to log in
        next = driver.find_element_by_name(
            'ctl00$mainContent$Tab1$next_text_button_button')
        next.click()

    def _log_in(self, driver):
        self._log_in_customer_number(driver)
        self._log_in_pin_and_password(driver)

    def _navigate_to_downloads_page(self, driver):
        self._switch_to_security_frame(driver)
        driver.find_element_by_xpath('//*[text()="Statements"]') \
              .click()
        i = 'ctl00_mainContent_SS1AALDAnchor'  # Download/export transactions
        driver.find_element_by_id(i) \
              .click()

    def _initiate_download(self, driver):
        period = Select(driver.find_element_by_name('ctl00$mainContent$SS6SPDDA'))
        period.select_by_visible_text('Last 1 month')

        format = Select(driver.find_element_by_name('ctl00$mainContent$SS6SDDDA'))
        format.select_by_visible_text('Microsoft Money (OFX file)')

        next = driver.find_element_by_name('ctl00$mainContent$FinishButton_button')
        next.click()

        download = driver.find_element_by_name(
            'ctl00$mainContent$SS7-LWLA_button_button')
        download.click()
