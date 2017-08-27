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
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not(self == other)

    def uuid(self):
        return self._uuid

    def extract_secrets(self, secrets):
        new_secrets = {}
        for name in self._secrets.keys():
            value = secrets[name]
            new_secrets[name] = value
        self._secrets = new_secrets
        self._extract_secrets_success = True

    def secret(self, name):
        return self._secrets[name]

    def all_secrets(self):
        return self._secrets.keys()
