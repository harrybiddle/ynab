import yaml
from schema import Optional, Or, Schema

from .banks.amex_com import Amex
from .banks.dkb_de import DKB
from .banks.halifax_com import Halifax
from .banks.hsbc_com import HSBC
from .banks.natwest_com import Natwest

BANKS = {"amex": Amex, "halifax": Halifax, "hsbc": HSBC, "natwest": Natwest, "dkb": DKB}
_BANK_SCHEMA = {
    "type": Or(*BANKS.keys()),
    Optional("secrets_keys"): {str: str},
    "target": {"budget_id": str, "account_id": str},
    Optional(str): object,
}
_YNAB_SCHEMA = {"secrets_keys": {"access_token": str}}
_KEYRING_SCHEMA = {"username": str}
_CONFIG_SCHEMA = Schema(
    {"banks": [_BANK_SCHEMA], "ynab": _YNAB_SCHEMA, "keyring": _KEYRING_SCHEMA}
)


def parse_config(config):
    """ Raises: SchemaError if the supplied configuration is invalid
    """
    return _CONFIG_SCHEMA.validate(config)


def load_config(config_file):
    with open(config_file) as conf:
        loaded_config = yaml.safe_load(conf)
    return parse_config(loaded_config)
