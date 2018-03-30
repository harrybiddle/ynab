import fileutils

from bank import Bank


class HSBC(Bank):

    full_name = 'HSBC'

    def __init__(self, config, secrets):
        super(HSBC, self).__init__(secrets)
        self.validate_secrets('memorable_question', 'security_code')
        self.username = config['username']

    def download_transactions(self, driver, dir):
        self._start_download(driver)
        return self._wait_until_download_complete(dir)

    def _start_download(self, driver):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _wait_until_download_complete(self, dir):
        return fileutils.wait_for_file(dir, '.qfx')[0]

    def _go_to_website(self, driver):
        driver.get('https://www.hsbc.co.uk/')
        assert 'HSBC' in driver.title

        # go to the login
        driver.find_element_by_class_name('redBtn').click()

    def _log_in(self, driver):
        username = driver.switch_to_active_element()
        username.send_keys(self.username)

        # get to password submission point
        driver.find_element_by_class_name('submit_input').click()

        # fill in memorable question and 2FA
        memorable = driver.find_element_by_id('memorableAnswer')
        memorable.send_keys(self.secret('memorable_question'))

        code = driver.find_element_by_id('idv_OtpCredential')
        code.send_keys(self.secret('security_code'))

        # complete login
        driver.find_element_by_class_name('submit_input').click()

    def _navigate_to_downloads_page(self, driver):
        # only grabs main account
        driver.find_element_by_id('dapViewMoreDownload').click()

    def _initiate_download(self, driver):
        driver.find_element_by_id('dapViewMoreDownload').click()

        # select ofx for download
        id = '$group_gpib_acct_bijit_AccountFilterPayments_2_ofx'
        driver.find_element_by_id(id).click()

        # TODO can't get download to kick off :(
        driver.find_element_by_class_name('btnSecondary').click()
