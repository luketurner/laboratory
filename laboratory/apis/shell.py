import subprocess
from typing import List

from ..errors import ApplicationException


def shell(args: List[str]):
    code = subprocess.call(args)
    if code > 0:
        raise ApplicationException("Shell command returned nonzero exit code {}: {}".format(code, " ".join(args)))
    return code
