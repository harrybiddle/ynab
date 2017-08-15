import collections
import fileutils
from bank import Bank
from selenium.webdriver import ActionChains

class HSBC (Bank) :
    hsbc_secret = collections.namedtuple('Secret', ('hsbc_username hsbc_memorable_question hsbc_security_code ynab_password'))

    full_name = "HSBC"
    
    def prompt(self):
        print ('Enter a semicolon separated list of hsbc username, '
               'hsbc memorable question, hsbc security code, and ynab password')

    def parse_secret(self, semicolon_separated_text):
        self.secret = self.hsbc_secret(*semicolon_separated_text.split(';'))

    def download_transactions(self, driver, dir):
        self._start_download(driver)
        return self._wait_until_download_complete(dir)

    def _start_download(self, driver):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _wait_until_download_complete(self, dir):
        return fileutils.wait_for_file(dir, '.qfx')

    def _go_to_website(self, driver):
        driver.get('https://www.hsbc.co.uk/')
        assert "HSBC" in driver.title

        # go to the login
        driver.find_element_by_class_name('redBtn').click()
        
    def _log_in(self, driver):
        username = driver.switch_to_active_element()
        username.send_keys(self.secret.hsbc_username)

        # get to password submission point 
        driver.find_element_by_class_name("submit_input").click()

        # fill in memorable question and 2FA
        memorable = driver.find_element_by_id("memorableAnswer")
        memorable.send_keys(self.secret.hsbc_memorable_question);

        code = driver.find_element_by_id("idv_OtpCredential");
        code.send_keys(self.secret.hsbc_security_code)

        # complete login
        driver.find_element_by_class_name("submit_input").click()
        
    def _navigate_to_downloads_page(self, driver):
        # only grabs main account
        driver.find_element_by_id("dapViewMoreDownload").click()
       
    def _initiate_download(self, driver):
        driver.find_element_by_id('dapViewMoreDownload').click()

        # select ofx for download
        driver.find_element_by_id("$group_gpib_acct_bijit_AccountFilterPayments_2_ofx").click()
            
        # TODO can't get download to kick off :(
        driver.find_element_by_class_name("btnSecondary").click()
