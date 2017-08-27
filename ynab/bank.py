import uuid

class Bank(object):

    def __init__(self, secrets=[]):
        self._uuid = str(uuid.uuid4())
        self._secrets = dict([(s, None) for s in secrets])
        self._extract_secrets_success = False

    def __hash__(self):
        return hash(self.uuid())

    def __eq__(self, other):
        return self.uuid() == other.uuid()

    def __ne__(self, other):
        return not(self == other)

    def uuid(self):
        ''' Returns the unique UUID for this object, as a string
        '''
        return self._uuid

    def extract_secrets(self, secrets):
        ''' Takes a map of secret name -> secret value and stores
        the values in this object '''
        new_secrets = {}
        for name in self._secrets.keys():
            value = secrets[name]
            new_secrets[name] = value
        self._secrets = new_secrets
        self._extract_secrets_success = True

    def secret(self, name):
        ''' Return the value of the given secret.

        Args:
            name: the name of the secret (string)

        Raises:
            KeyError: If this secret wasn't named in the original
                construction of the Bank object.

        Returns:
            The value of the secret. If the secret hasn't yet been supplied
                the value will be None.
        '''
        return self._secrets[name]

    def all_secrets(self):
        ''' Return a list of all secrets named in the original construction
        of the Bank object.
        '''
        return self._secrets.keys()
