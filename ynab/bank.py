import uuid


class ObjectWithSecrets:
    def __init__(self, secrets, *args, **kwargs):
        self._secrets = secrets or dict()

    @classmethod
    def from_config(cls, config, keyring):
        secrets_keys = config.pop("secrets_keys", {})
        secrets = keyring.get_secrets(secrets_keys)
        return cls(config, secrets)

    def validate_secrets(self, *expected):
        """ Raises an AssertionError if the list of secret names (given as
        function arguments) doesn't match exactly the secrets we have """
        given = self._secrets.keys()
        error_msg = (
            "Given secrets differ from expected. Received\n  {}\nbut " "expected\n  {}"
        ).format(str(given), str(expected))
        assert set(expected) == set(given), error_msg

    def secret(self, name):
        """ Return the value of the given secret, e.g.

            >> self.secret('password')
            'pass123'

        Raises:
            KeyError if the secret doesn't exist
        """
        return self._secrets[name]


class Bank(ObjectWithSecrets):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._uuid = str(uuid.uuid4())

    def __hash__(self):
        return hash(self.uuid())

    def __eq__(self, other):
        return self.uuid() == other.uuid()

    def __ne__(self, other):
        return not (self == other)

    def uuid(self):
        """ Returns the unique UUID for this object, as a string
        """
        return self._uuid
