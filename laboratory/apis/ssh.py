from paramiko.client import SSHClient, AutoAddPolicy
from typing import List

def ssh(host: str, cmds: List[List[str]], username: str):
    client = SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(AutoAddPolicy)
    try:
        print(f"executing commands on host: {username}@{host}")
        client.connect(
            hostname=host,
            username=username
        )
        
        for cmd in cmds:
            cmdstr = " ".join(f"'{x}'" for x in cmd)
            print(f"> {cmdstr}")
            stdin, stdout, stderr = client.exec_command(cmdstr)
            for line in stdout:
                print("    ", line, end="")
            for line in stderr:
                print("  E ", line, end="")
    finally:
        client.close()