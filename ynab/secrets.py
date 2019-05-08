import keyring


class Keyring:
    def __init__(self, username):
        self.username = username

    def get_secrets(self, secret_names_and_keys):
        """ Performs a lookup in the system keyring for the given secret(s).

        Args:
            secret_names_and_keys: a dictionary mapping secret name to the key in
                the system keyring, for example {'password': 'ynab_password'}

        Returns:
            A dictionary of secret_name to the value, for example
                {'password': 'pass1234'}

        Raises:
            KeyError: at least one key doesn't exist in the keyring
        """
        ret = {}
        for secret_name, service_name in secret_names_and_keys.items():
            secret_value = keyring.get_password(service_name, self.username)
            if secret_value is None:
                raise KeyError(
                    ("The key {} for user {} cannot be found in the " "keyring").format(
                        service_name, self.username
                    )
                )
            ret[secret_name] = secret_value
        return ret
