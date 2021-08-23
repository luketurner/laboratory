from .apis.ansible import run_playbook
from .apis.script import script
from .apis.assets import download_asset, get_asset_path
from .apis.ssh import ssh
from .config import get_in_config

import ipaddress

from toolz.itertoolz import nth

def cluster_router_ip():
    return get_in_config(["cluster", "net", "router_ip"])

def cluster_node_ip(node_num):
    cidr = get_in_config(["cluster", "net", "cidr"])
    network = ipaddress.ip_network(cidr)
    return str(nth(node_num - 1, network.hosts()))

def cluster_node_hostname(node_num):
    return f"pi{node_num}"

def prep_node(node_num, device):
    download_asset('archive_archlinuxarm_aarch64')
    script('mksdcard.sh', [
        '--device', device,
        '--public-key', get_in_config(["admin_public_key"]),
        '--archive', get_asset_path('archive_archlinuxarm_aarch64'),
        '--ip-address', cluster_node_ip(node_num),
        '--router-ip', cluster_router_ip(),
        '--hostname', cluster_node_hostname(node_num)
    ], sudo=True)

def provision_node(node_num):
    download_asset('binary_k0s')
    public_key = get_in_config(["admin_public_key"])
    node_ip = cluster_node_ip(node_num)
    # Install python over SSH -- since it's needed for ansible
    ssh(
        host=node_ip,
        username="root",
        cmds=[
            ["pacman-key", "--init"],
            ["pacman-key", "--populate", "archlinuxarm"],
            ["pacman", "-Sy", "--noconfirm", "python"]
        ]
    )
    run_playbook(
        playbook="cluster-node-rpi4-k0s.yml",
        inventory=[node_ip],
        extra_vars={
            "admin_user": get_in_config(["admin_user"]),
            "playbook_user": "root",
            "k0s_binary": get_asset_path("binary_k0s"),
            "ssh_key_file": public_key,
            "k0s_master": node_num == 1 
        }
    )

def cluster_status():
    raise NotImplementedError()

def cluster_kubecfg():
    raise NotImplementedError()
