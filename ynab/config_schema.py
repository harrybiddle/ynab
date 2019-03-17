import yaml
from schema import And, Optional, Or, Schema

from ynab.amex_com import Amex
from ynab.dkb_de import DKB
from ynab.halifax_com import Halifax
from ynab.hsbc_com import HSBC
from ynab.natwest_com import Natwest
from ynab.sparkasse_de import SparkasseHeidelberg

BANKS = {
    "amex": Amex,
    "halifax": Halifax,
    "hsbc": HSBC,
    "natwest": Natwest,
    "sparkasse-heidelberg": SparkasseHeidelberg,
    "dkb": DKB,
}

_SOURCE_SCHEMA = {
    "type": Or(*BANKS.keys()),
    Optional("secrets_keys"): {str: str},
    Optional(str): object,
}
_TARGET_SCHEMA = {
    "budget": And(str, len),
    "account": And(str, len),
    Optional("id"): object,
}
_YNAB_SCHEMA = {
    "email": And(str, len),
    "targets": [_TARGET_SCHEMA],
    "secrets_keys": {"password": str},
}
_KEYRING_SCHEMA = {"username": str}
_CONFIG_SCHEMA = Schema(
    {"sources": [_SOURCE_SCHEMA], "ynab": _YNAB_SCHEMA, "keyring": _KEYRING_SCHEMA}
)


def parse_config(config):
    """ Raises: SchemaError if the supplied configuration is invalid
    """
    return _CONFIG_SCHEMA.validate(config)


def load_config(config_file):
    with open(config_file) as conf:
        loaded_config = yaml.load(conf)
    return parse_config(loaded_config)
