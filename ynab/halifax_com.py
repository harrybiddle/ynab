import collections
import fileutils
import re
import time

from bank import Bank
from selenium.webdriver import ActionChains

class Halifax (Bank) :
    halifax_secret = collections.namedtuple('Secret', ('halifax_username halifax_password halifax_challenge ynab_password'))

    full_name = 'Halifax'

    def prompt(self):
        print ('Enter a semicolon separated list of your halifax username, '
               'halifax password, halifax challenge, and ynab password')

    def parse_secret(self, semicolon_separated_text):
        self.secret = self.halifax_secret(*semicolon_separated_text.split(';'))

    def download_transactions(self, driver, dir):
        self._start_download(driver)
        paths = self._wait_until_download_complete(dir)

        return self._invert_files(paths)

    def _start_download(self, driver):
        self._go_to_website(driver)
        self._log_in(self.secret, driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _wait_until_download_complete(self, dir):
        return fileutils.wait_for_file_with_prefix(dir, '.qif', '5253030007970668')

    # Used to invert the sign of transactions in the downloaded files so ynab interprets the transactions correctly
    def _invert_files(self, paths):
        toReturn = []
        for path in paths:
            new_file_path = path[:-4] + '_fixed.qif';
            new_file = open(new_file_path, 'w')
            for count, line in enumerate(open(path, 'r')):
                if ((count + 1) % 4 == 0):
                    if (line.startswith('T-')):
                        new_file.write('T' + line[2:])
                    else:
                        new_file.write('T-' + line[1:])
                else:
                    new_file.write(line)
            toReturn.append(new_file_path)

        return toReturn

    def _go_to_website(self, driver):
        driver.get('https://www.halifax-online.co.uk')
        assert 'Halifax' in driver.title

    def _log_in(self, secret, driver):
        user_id = driver.find_element_by_name('frmLogin:strCustomerLogin_userID')
        user_id.send_keys(secret.halifax_username)

        password = driver.find_element_by_id('frmLogin:strCustomerLogin_pwd')
        password.send_keys(secret.halifax_password)

        # click through to log in
        loginButton = driver.find_element_by_id('frmLogin:btnLogin2')
        loginButton.click()

        self._complete_challenge(driver)

    def _complete_challenge(self, driver):
        # Please enter characters X, Y and Z from your memorable information then
        # click the continue button.\nWe will never ask you to enter your FULL
        # memorable information.\nThis sign in step improves your security.
        description = driver.find_element_by_class_name('inner').text

        description = description[:34]
        match = re.match('Please enter characters ([1-8]), ([1-8]) and ([1-8])', description)

        indexes = [int(match.group(1)) - 1, int(match.group(2)) - 1, int(match.group(3)) - 1]
        chars = ''.join(map(self.secret.halifax_challenge.__getitem__, indexes))

        challenge_selectors = [
            driver.find_element_by_name('frmentermemorableinformation1:strEnterMemorableInformation_memInfo1'),
            driver.find_element_by_name('frmentermemorableinformation1:strEnterMemorableInformation_memInfo2'),
            driver.find_element_by_name('frmentermemorableinformation1:strEnterMemorableInformation_memInfo3')]

        for char, selector in zip(chars, challenge_selectors):
            selector.send_keys(char)

        driver.find_element_by_id('frmentermemorableinformation1:btnContinue').click()

    def _navigate_to_downloads_page(self, driver):
        driver.find_element_by_id('lnkAccFuncs_viewStatement_des-m-sat-xx-1').click()

    def _initiate_download(self, driver):
        self._get_earlier_page(driver)
        self._get_earlier_page(driver)

    def _get_earlier_page(self, driver):
        earlier_button = driver.find_element_by_id('lnkEarlierBtnMACC')
        driver.execute_script('arguments[0].scrollIntoView()', earlier_button)
        earlier_button.click()

        # wait for it to load
        time.sleep(2)

        driver.find_element_by_id('lnkExportStatementSSR').click()

        # select download mechanic
        driver.find_element_by_id('export-format').send_keys('p')

        driver.find_element_by_id('creditcardstatment:ccstmt:export-statement-form:btnExport').click()
        driver.find_element_by_class_name('overlay-close').click()
