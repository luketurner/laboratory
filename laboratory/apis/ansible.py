import os.path
from typing import Dict, List
from .shell import shell
from ..config import get_in_config

def run_playbook(playbook: str, inventory: List[str], extra_vars: Dict[str, str]):
    shell([
        "ansible-playbook",
        os.path.join('playbooks', playbook),
        "--private-key", get_in_config(["admin_private_key"]),
        f"--inventory={','.join(inventory)},"
    ] + [
        f"--extra-vars={k}={v}" for k, v in extra_vars.items()
    ])