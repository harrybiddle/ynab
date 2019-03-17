import glob
import os.path

from polling import poll

_WAIT_FOR_FILE_DOWNLOAD_SECONDS = 10
_WAIT_FOR_FILE_DOWNLOAD_POLL_SECONDS = 1


def wait_for_file(dir, file_extension):
    return _wait_for_file(dir, "*" + file_extension)


def wait_for_file_with_prefix(dir, file_extension, file_prefix):
    """ Waits for _WAIT_FOR_FILE_DOWNLOAD_SECONDS seconds until a
    file exists in the given directory.  When it does, returns the
    full file path to that file, or the first file if there are many
    """
    return _wait_for_file(dir, file_prefix + "*" + file_extension)


def _wait_for_file(dir, path):
    g = os.path.join(dir, path)
    poll(
        lambda: glob.glob(g),
        timeout=_WAIT_FOR_FILE_DOWNLOAD_SECONDS,
        step=_WAIT_FOR_FILE_DOWNLOAD_POLL_SECONDS,
    )
    return glob.glob(g)
