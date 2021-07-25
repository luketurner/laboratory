from typing import Dict, List
from .shell import shell

def run_playbook(playbook: str, inventory: List[str], extra_vars: Dict[str, str]):
    shell([
        "ansible-playbook",
        playbook,
        f"-inventory={','.join(inventory)}"
    ] + [
        f"--extra-vars={k}={v}" for k, v in extra_vars.items()
    ])