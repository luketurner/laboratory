import os.path

from typing import List
from .shell import shell

def script(name: str, args: List[str], sudo = False):
    return shell([os.path.join('scripts', name)] + args, sudo=sudo)