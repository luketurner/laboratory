from paramiko.client import SSHClient, AutoAddPolicy
from typing import List
from ..config import get_in_config


def ssh(host: str, cmds: List[List[str]], username: str, return_stdio=False):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy)
    results = []
    try:
        print(f"executing commands on host: {username}@{host}")
        client.connect(
            hostname=host,
            username=username,
            key_filename=get_in_config(["admin_private_key"])
        )
        
        for cmd in cmds:
            cmdstr = " ".join(f"'{x}'" for x in cmd)
            if len(cmdstr) > 120:
                print(">", cmdstr[0:30], "... [SNIP] ...", cmdstr[-30:-1])
            else:
            print(f"> {cmdstr}")
            stdin, stdout, stderr = client.exec_command(cmdstr)
            if return_stdio:
                results.append((stdout.read(), stderr.read()))            
            else:
            for line in stdout:
                print("    ", line, end="")
            for line in stderr:
                print("  E ", line, end="")
        return results
    finally:
        client.close()