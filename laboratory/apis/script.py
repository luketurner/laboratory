import os.path

from typing import List
from .shell import shell

def script(name: str, args: List[str]):
    shell([os.path.join('scripts', name)] + args)