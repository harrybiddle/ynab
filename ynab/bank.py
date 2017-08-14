import os.path
from glob import glob
from polling import poll
from getpass import getpass

_WAIT_FOR_FILE_DOWNLOAD_SECONDS = 10
_WAIT_FOR_FILE_DOWNLOAD_POLL_SECONDS = 1

class Bank:
    def get_secret_text_from_user(self):
        self.prompt()
        user_input = getpass()
        return self.parse_secret(user_input)

    def wait_for_file(self, dir, file_extension):
        return self._wait_for_file(dir, '*' + file_extension)

    def wait_for_file_with_prefix(self, dir, file_extension, file_prefix):
        return self._wait_for_file(dir, file_prefix + '*' + file_extension)

    def _wait_for_file(self, dir, path):
        g = os.path.join(dir, path)
        poll(lambda: glob(g),
             timeout=_WAIT_FOR_FILE_DOWNLOAD_SECONDS,
             step=_WAIT_FOR_FILE_DOWNLOAD_POLL_SECONDS)
        return glob(g)
