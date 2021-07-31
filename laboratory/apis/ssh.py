from paramiko.client import SSHClient
from typing import List

def ssh(host: str, cmds: List[List[str]], username: str):
    client = SSHClient()
    client.load_system_host_keys()
    try:
        client.connect(
            hostname=host,
            username=username
        )
        return [client.exec_command(cmd) for cmd in cmds]
    finally:
        client.close()