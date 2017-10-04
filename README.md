YNAB
====

Selenium automation to download transactions from online banking websites
then upload them to YouNeedABudget.com.

Installation
------------

Requirements:

1. [Google Chrome](https://www.google.com/chrome).
1. [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/). For a Mac with [Homebrew](https://brew.sh), this can be done with `brew install chromedriver`. 
1. Python 2.7.

Optional:

1. [pip](https://pip.pypa.io) for easy installation of the script.
1. [1Password](https://1password.com/) and [sudolikeaboss](https://github.com/ravenac95/sudolikeaboss) for easy password entry.

To install the script:

```bash
python setup.py bdist_wheel
pip install dist/ynab*.whl
```

You will need to make sure that directory containing the binary (as displayed with `pip show -f ynab`) is on your `PATH`. For a Mac this can be done with

```bash
echo 'PATH=$PATH:~/Library/Python/2.7/bin/' >> ~/.bash_profile
hash -r
```

Usage
-----

Create a file `~/.ynab.conf` that contains the banks you wish to fetch ("sources") and the some information about where to upload it on YNAB. The full list of available configuration is as follows. You should supply *exactly one source*:

```yml
sources:
  - type: amex
    username: john.smith
  - type: halifax
    username: john.smith
  - type: hsbc
    username: john.smith
  - type: natwest
    customer_number: 12345678
ynab:
  email: email@domain.com
  targets:
    - budget: My Budget
      account: My Account
```

Then run the command `ynab`. It will prompt you for a semicolon-separated list of secrets (passwords, etc).
These are requested in the order that they were written in the configuration file.

Development
-----------

To run tests:

```bash
python setup.py test
```
