import os.path
import re
import time

from ynab import fileutils
from ynab.bank import Bank

CHALLENGE_DESCRIPTION_CLASS_NAME = "inner"


class Halifax(Bank):
    full_name = "Halifax"

    def __init__(self, config, secrets):
        super().__init__(secrets)
        self.validate_secrets("password", "challenge")
        self.username = config["username"]

    def download_transactions(self, driver, dir):
        self._start_download(driver)
        paths = self._wait_until_download_complete(dir)

        return self._invert_files(paths)[0]

    def _start_download(self, driver):
        self._go_to_website(driver)
        self._log_in(driver)
        self._navigate_to_downloads_page(driver)
        self._initiate_download(driver)

    def _wait_until_download_complete(self, dir):
        return fileutils.wait_for_file_with_prefix(dir, ".qif", "5253030007970668")

    def _invert_files(self, paths):
        """ Reads files of bank transaction from disks, inverts the sign of the
        transaction amounts, and writes them out to another file.
        Args:
            paths: a list of file paths to modify

        Returns: a list of the written files. For an input file a.qif, the
            output file will be a_fixed.qif
        """

        to_return = []
        for path in paths:
            new_path = "_fixed".join(os.path.splitext(path))
            print(new_path)
            with open(new_path, "w") as new_file, open(path) as file:
                for count, line in enumerate(file):
                    if (count + 1) % 4 == 0:
                        if line.startswith("T-"):
                            new_file.write("T" + line[2:])
                        else:
                            new_file.write("T-" + line[1:])
                    else:
                        new_file.write(line)
            to_return.append(new_path)

        return to_return

    def _go_to_website(self, driver):
        driver.get("https://www.halifax-online.co.uk")
        assert "Halifax" in driver.title

    def _log_in(self, driver):
        n = "frmLogin:strCustomerLogin_userID"
        user_id = driver.find_element_by_name(n)
        user_id.send_keys(self.username)

        password = driver.find_element_by_id("frmLogin:strCustomerLogin_pwd")
        password.send_keys(self.secret("password"))

        # click through to log in
        loginButton = driver.find_element_by_id("frmLogin:btnLogin2")
        loginButton.click()

        self._complete_challenge(driver)

    def _complete_challenge(self, driver):
        # Please enter characters X, Y and Z from your memorable information
        # then click the continue button.\nWe will never ask you to enter your
        # FULL memorable information.\nThis sign in step improves your
        # security.
        description = driver.find_element_by_class_name(
            CHALLENGE_DESCRIPTION_CLASS_NAME
        ).text  # noqa

        description = description[:34]
        match = re.match(
            ("Please enter characters ([1-8]), ([1-8]) " "and ([1-8])"), description
        )

        indexes = [
            int(match.group(1)) - 1,
            int(match.group(2)) - 1,
            int(match.group(3)) - 1,
        ]
        chars = "".join(map(self.secret("challenge").__getitem__, indexes))

        m1 = "frmentermemorableinformation1:strEnterMemorableInformation_" "memInfo1"
        m2 = "frmentermemorableinformation1:strEnterMemorableInformation_" "memInfo2"
        m3 = "frmentermemorableinformation1:strEnterMemorableInformation_" "memInfo3"
        challenge_selectors = [
            driver.find_element_by_name(m1),
            driver.find_element_by_name(m2),
            driver.find_element_by_name(m3),
        ]

        for char, selector in zip(chars, challenge_selectors):
            selector.send_keys(char)

        id = "frmentermemorableinformation1:btnContinue"
        driver.find_element_by_id(id).click()

    def _navigate_to_downloads_page(self, driver):
        driver.find_element_by_id("lnkAccFuncs_viewStatement_des-m-sat-xx-1").click()

    def _initiate_download(self, driver):
        self._get_earlier_page(driver)
        self._get_earlier_page(driver)

    def _get_earlier_page(self, driver):
        earlier_button = driver.find_element_by_id("lnkEarlierBtnMACC")
        driver.execute_script("arguments[0].scrollIntoView()", earlier_button)
        earlier_button.click()

        # wait for it to load
        time.sleep(2)

        driver.find_element_by_id("lnkExportStatementSSR").click()

        # select download mechanic
        driver.find_element_by_id("export-format").send_keys("p")

        id = "creditcardstatment:ccstmt:export-statement-form:btnExport"
        driver.find_element_by_id(id).click()
        driver.find_element_by_class_name("overlay-close").click()
