from getpass import getpass

class Bank:
    def get_secret_text_from_user(self):
        self.prompt()
        user_input = getpass()
        return self.parse_secret(user_input)
