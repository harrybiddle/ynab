YNAB
====

Selenium automation to download transactions from online banking websites
then upload them to YouNeedABudget.com.

Installation
------------

Requirements:

1. A supported backend for [keyring](https://pypi.python.org/pypi/keyring). The Mac Keychain or Windows Credential Manager will do.
1. [Google Chrome](https://www.google.com/chrome).
1. [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/). For a Mac with [Homebrew](https://brew.sh), this can be done with `brew install chromedriver`.
1. Python 2.7.

Optional:

1. [pip](https://pip.pypa.io) for easy installation of the script.

To install the script:

```bash
pip install --user -r requirements.txt
python setup.py bdist_wheel
pip install --user dist/ynab*.whl
```

You will need to make sure that directory containing the binary (as displayed with `pip show -f ynab`) is on your `PATH`. For a Mac this can be done with

```bash
echo 'PATH=$PATH:~/Library/Python/2.7/bin/' >> ~/.bash_profile
source ~/.bash_profile
hash -r
```

Configuration
-------------

1. Create a file `~/.ynab.conf` with the following contents. Fill in any entries in angled brackets (`<`, `>`).
   Don't fill in any of the `secrets_keys` entires, we'll put this in your keyring in the next step!

   ```yml
   ynab:
     email: <email@domain.com>
     secrets_keys:
       password: ynab_password
     targets:
       - budget: <My Budget>
         account: <My Account>
   keyring:
     username: ynab
   sources:
     - type: <see below...>
   ```

2. Choose *one bank* from the below list, fill in any entries in angled brackets, and add it to `~/.ynab.conf`.
   Again, don't fill in any of the `secrets_keys` entires!

   - Amex:
     ```yml
     sources:
       - type: amex
         username: <amex_username>
         secrets_keys:
           password: amex_password
     ```

   - Halifax:
     ```yml
     sources:
       - type: halifax
         username: <halifax_username>
         secrets_keys:
           password: halifax_password
           challenge: halifax_challenge_password
     ```

   - HSBC:
     ```yml
     sources:
       - type: hsbc
         username: <hsbc_username>
         secrets_keys:
           memorable_question: hsbc_memorable_question
           security_code: hsbc_security_code
      ```

   - Natwest:
     ```yml
     sources:
       - type: natwest
         customer_number: <natwest_customer_number>
         secrets_keys:
           password: natwest_password
           pin: natwest_pin
     ```

   - Sparkasse-Heidelberg:
     ```yml
     sources:
       - type: sparkasse-heidelberg
         username: <sparkasse_username>
         secrets_keys:
           pin: sparkasse_pin
     ```

1. Open your keyring backend---on a Mac, this will be the KeyChain app--and create one entry for each secret for your bank and one for your YNAB password with the account 'ynab'.

   For example, if you have chosen Amex you will put in two entries:

   1. Keychain Item Name: `amex_password`, Account Name: `ynab`, Password: `<your amex password>`
   1. Keychain Item Name: `ynab_password`, Account Name: `ynab`, Password: `<your ynab password>`

Usage
-------------

Simply run the command `ynab`.

Development
-----------

To run tests:

```bash
pip install --user -r requirements.txt
python setup.py test
```

To run a specific test suite:

```
python setup.py test -s tests.test_ynab.TestLoggedDriver
```

