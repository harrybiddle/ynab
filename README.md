YNAB
====

Scrapes transactions from online banking portals and uploads them to YouNeedABudget.com.

Installation
------------

The project isn't on PyPI

Requirements:

1. A supported backend for [keyring](https://pypi.python.org/pypi/keyring). The Mac Keychain or Windows Credential Manager will do.
1. [Google Chrome](https://www.google.com/chrome).
1. [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/). For a Mac with [Homebrew](https://brew.sh), this can be done with `brew install chromedriver`.
1. Python 3.7 and [poetry](https://poetry.eustace.io/)

To install ynab run the following:

```bash
rm -rf dist/*
poetry build --format sdist
pip3 install --user dist/*
```

Configuration
-------------

1. Create a file `~/.ynab.conf` with the following contents. Fill in any entries in angled brackets (`<`, `>`).
   The `secrets_keys` entry should not contain any actual secrets, insert it as written:

   ```yml
   ynab:
     secrets_keys:
       access_token: ynab_access_token
   keyring:
     username: ynab
   ```

1. [Head over to YouNeedABudget to generate a "personal access token"](https://api.youneedabudget.com/#authentication-overview).

1. Find out the budget id and account id that you would like to upload transactions to by using their API.

2. Choose *one bank* from the below list, fill in any entries in angled brackets, and add it to `~/.ynab.conf`.
   Values in `<..>` should be filled out but everything else, particularly the "secrets_keys" section, should be pasted in verbatim.

   - Amex:
     ```yml
     sources:
       - type: amex
         username: <your amex username>
         secrets_keys:
           password: amex_password
         target:
           budget_id: <your budget id>
           account_id: <your account id>
     ```

   - Halifax:
     ```yml
     sources:
       - type: halifax
         username: <your halifax username>
         secrets_keys:
           password: halifax_password
           challenge: halifax_challenge_password
         target:
           budget_id: <your budget id>
           account_id: <your account id>
     ```

   - HSBC:
     ```yml
     sources:
       - type: hsbc
         username: <your hsbc username>
         secrets_keys:
           memorable_question: hsbc_memorable_question
           security_code: hsbc_security_code
         target:
           budget_id: <your budget id>
           account_id: <your account id>
      ```

   - Natwest:
     ```yml
     sources:
       - type: natwest
         customer_number: <your natwest customer number>
         secrets_keys:
           password: natwest_password
           pin: natwest_pin
         target:
           budget_id: <your budget id>
           account_id: <your account id>
     ```

   - DKB:
     ```yml
     sources:
       - type: dkb
         secrets_keys:
           anmeldename: dkb_anmeldename
           pin: dkb_pin
         target:
           budget_id: <your budget id>
           account_id: <your account id>
     ```

1. Open your keyring backend---on a Mac, this will be the KeyChain app--and create one entry for each secret for your bank and one for your access token.
   For example, if you have chosen Amex you will put in two entries

   - Keychain Item Name: `amex_password`, Account Name: `ynab`, Password: `<your amex password>`
   - Keychain Item Name: `ynab_access_token`, Account Name: `ynab`, Password: `<your ynab personal access token>`

Usage
-------------

Simply run the command `ynab`.

Development
-----------

Dependencies are installed using poetry:

```bash
poetry install
```

To run tests:

```
poetry run python -m unittest discover
```

All files should be processed with [black](https://black.readthedocs.io/en/stable/) and [isort](https://github.com/timothycrosley/isort) before committing:

```
poetry run black
poetry run isort -rc
```

