import selenium.webdriver.support.ui as ui

from bank import Bank
import fileutils

# text box on first page to enter customer number
CUSTOMER_NUMBER = 'ctl00$mainContent$LI5TABA$DBID_edit'

# button to log in
LOG_IN_BUTTON = 'ctl00$mainContent$Tab1$next_text_button_button'

# these web elements specify which digits of the pin and characters of the
# password should be provided
PIN_DIGIT_1 = 'ctl00_mainContent_Tab1_LI6DDALALabel'
PIN_DIGIT_2 = 'ctl00_mainContent_Tab1_LI6DDALBLabel'
PIN_DIGIT_3 = 'ctl00_mainContent_Tab1_LI6DDALCLabel'
PASSWORD_CHARACTER_1 = 'ctl00_mainContent_Tab1_LI6DDALDLabel'
PASSWORD_CHARACTER_2 = 'ctl00_mainContent_Tab1_LI6DDALELabel'
PASSWORD_CHARACTER_3 = 'ctl00_mainContent_Tab1_LI6DDALFLabel'

# these are the text boxes where you enter the digits and characters
PIN_TETXBOX_1 = 'ctl00$mainContent$Tab1$LI6PPEA_edit'
PIN_TETXBOX_2 = 'ctl00$mainContent$Tab1$LI6PPEB_edit'
PIN_TETXBOX_3 = 'ctl00$mainContent$Tab1$LI6PPEC_edit'
PASSWORD_TEXTBOX_1 = 'ctl00$mainContent$Tab1$LI6PPED_edit'
PASSWORD_TEXTBOX_2 = 'ctl00$mainContent$Tab1$LI6PPEE_edit'
PASSWORD_TEXTBOX_3 = 'ctl00$mainContent$Tab1$LI6PPEF_edit'

# an iframe on many pages that you have to switch to
SECURITY_FRAME = 'ctl00_secframe'

# Statements on left sidebar
STATEMENTS = '//*[text()="Statements"]'

# 'Download/Export Transactions'
DOWNLOAD_TRANSACTIONS_BUTTON = 'ctl00_mainContent_SS1AALDAnchor'

# 1 week, 1 month, etc
DOWNLOAD_PERIOD_DROPDOWN = 'ctl00$mainContent$SS6SPDDA'

# ofx, csv, etc
DOWNLOAD_FILE_TYPE_DROPDOWN = 'ctl00$mainContent$SS6SDDDA'

# 'next' page and 'download'
NEXT_BUTTON = 'ctl00$mainContent$FinishButton_button'
DOWNLOAD_BUTTON = 'ctl00$mainContent$SS7-LWLA_button_button'

class Natwest(Bank):

    full_name = 'Natwest'

    def __init__(self, config):
        super(Natwest, self).__init__(['pin', 'password'])
        self.customer_number = config['customer_number']

    def download_transactions(self, driver, dir):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)
        return fileutils.wait_for_file(dir, '.ofx')[0]

    def _go_to_website(self, driver):
        driver.get('https://www.nwolb.com')

    def _switch_to_security_frame(self, driver):
        driver.switch_to_default_content()
        driver.switch_to_frame(SECURITY_FRAME)

    def _log_in_customer_number(self, driver):
        self._switch_to_security_frame(driver)
        search_box = driver.find_element_by_name(CUSTOMER_NUMBER)
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
            driver.find_element_by_id(PIN_DIGIT_1).text,
            driver.find_element_by_id(PIN_DIGIT_2).text,
            driver.find_element_by_id(PIN_DIGIT_3).text]
        texts_requesting_password_chars = [
            driver.find_element_by_id(PASSWORD_CHARACTER_1).text,
            driver.find_element_by_id(PASSWORD_CHARACTER_2).text,
            driver.find_element_by_id(PASSWORD_CHARACTER_3).text]

        # extract the requested info from the secret
        subpin, subpassword = self._select_characters(
            texts_requesting_pin_digits,
            texts_requesting_password_chars)

        # find the text boxes on the page
        pin_text_boxes = [
            driver.find_element_by_name(PIN_TETXBOX_1),
            driver.find_element_by_name(PIN_TETXBOX_2),
            driver.find_element_by_name(PIN_TETXBOX_3)]
        password_text_boxes = [
            driver.find_element_by_name(PASSWORD_TEXTBOX_1),
            driver.find_element_by_name(PASSWORD_TEXTBOX_2),
            driver.find_element_by_name(PASSWORD_TEXTBOX_3)]

        # fill the text boxes
        for digit, box in zip(subpin, pin_text_boxes):
            box.send_keys(digit)
        for char, box in zip(subpassword, password_text_boxes):
            box.send_keys(char)

        driver.find_element_by_name(LOG_IN_BUTTON).click()

    def _log_in(self, driver):
        self._log_in_customer_number(driver)
        self._log_in_pin_and_password(driver)

    def _navigate_to_downloads_page(self, driver):
        self._switch_to_security_frame(driver)
        driver.find_element_by_xpath(STATEMENTS).click()
        driver.find_element_by_id(DOWNLOAD_TRANSACTIONS_BUTTON).click()

    def _initiate_download(self, driver):
        period = ui.Select(
            driver.find_element_by_name(DOWNLOAD_PERIOD_DROPDOWN))
        period.select_by_visible_text('Last 1 month')

        format = ui.Select(
            driver.find_element_by_name(DOWNLOAD_FILE_TYPE_DROPDOWN))
        format.select_by_visible_text('Microsoft Money (OFX file)')

        driver.find_element_by_name(NEXT_BUTTON).click()
        driver.find_element_by_name(DOWNLOAD_BUTTON).click()
