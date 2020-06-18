import subprocess

from .. import AppException


def shell(args):
    code = subprocess.call(args)
    if code > 0:
        raise AppException(
            "Shell command returned nonzero exit code {}: {}".format(
                code, " ".join(args)
            )
        )
    return code
