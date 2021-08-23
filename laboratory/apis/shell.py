import subprocess
from typing import List

from ..errors import ApplicationException


def shell(args: List[str], sudo = False, capture_output = False):
    result = subprocess.run(["sudo"] + args if sudo else args, capture_output=capture_output)
    if result.returncode > 0:
        raise ApplicationException("Shell command returned nonzero exit code {}: {}".format(result.returncode, " ".join(args)))
    return result
