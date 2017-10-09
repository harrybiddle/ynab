import keyring

def get_secrets(secret_names_and_keys, username):
    ''' Performs a lookup in the system keyring for the given secret(s).

    Args:
        secret_names_and_keys: a dictionary mapping secret name to the key in
            the system keyring, for example {'password': 'ynab_password'}

    Returns:
        A dictionary of secret_name to the value, for example
            {'password': 'pass1234'}

    Raises:
        KeyError: at least one key doesn't exist in the keyring
    '''
    ret = {}
    for secret_name, service_name in secret_names_and_keys.iteritems():
        secret_value = keyring.get_password(service_name, username)
        if secret_value is None:
            raise KeyError(('The key {} for user {} cannot be found in the '
                            'keyring').format(service_name, username))
        ret[secret_name] = secret_value
    return ret
