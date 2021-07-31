from .apis.ansible import run_playbook
from .apis.script import script
from .apis.assets import download_asset, get_asset_path
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

def prep_node(node_num, device, public_key):
    download_asset('archive_archlinuxarm_aarch64')
    script('mksdcard.sh', [
        '--device', device,
        '--public-key', public_key,
        '--archive', get_asset_path('archive_archlinuxarm_aarch64'),
        '--ip-address', cluster_node_ip(node_num),
        '--router-ip', cluster_router_ip(),
        '--hostname', cluster_node_hostname(node_num)
    ], sudo=True)

def provision_node(node_num, public_key):
    node_ip = cluster_node_ip(node_num)
    run_playbook(
        playbook="cluster-node-rpi4-k0s.yaml",
        inventory=[node_ip],
        extra_vars={
            "admin_user": get_in_config(["admin_user"]),
            "remote_user": "root",
            "k0s_binary": get_asset_path("binary_k0s"),
            "ssh_key_file": public_key,
            "k0s_master": node_num == 1 
        }
    )

def cluster_status():
    raise NotImplementedError()

def cluster_kubecfg():
    raise NotImplementedError()
