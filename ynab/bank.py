from getpass import getpass
import uuid

class Bank:
    def get_secret_text_from_user(self):
        self.prompt()
        user_input = getpass()
        return self.parse_secret(user_input)

    def generate_uuid(self):
    	if hasattr(self, '_uuid'):
    		raise RuntimeError('uuid already exists')
    	self._uuid = str(uuid.uuid4())

    def uuid(self):
    	return self._uuid
