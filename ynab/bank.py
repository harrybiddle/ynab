from getpass import getpass
import uuid

class Bank(object):

    def __init__(self, secrets=[]):
        self._uuid = str(uuid.uuid4())
        self._secrets = dict([(s, None) for s in secrets])
        self._extract_secrets_success = False

    def get_secret_text_from_user(self):
        self.prompt()
        user_inputs = getpass()
        return self.parse_secret(user_inputs)

    def uuid(self):
        return self._uuid

    def extract_secrets(self, secrets):
        our_secrets = secrets[self.uuid()]
        new_secrets = {}
        for name in self._secrets.keys():
            value = our_secrets[name]
            new_secrets[name] = value
        self._secrets = new_secrets
        self._extract_secrets_success = True

    def secret(self, name):
        assert (self._extract_secrets_success, Bank.failure_msg)
        return self._secrets[name]
