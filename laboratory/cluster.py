from .apis.ansible import run_playbook
from .apis.script import script
from .apis.assets import download_asset, get_asset_path
from .apis.ssh import ssh, calculate_ssh_style_subnet
from .apis.shell import shell
from .config import get_in_config
from .util import appdir

import yaml
import click

import ipaddress
import os.path
import itertools

from toolz.itertoolz import nth

def kubecfg_filename():
    return os.path.join(appdir(), "kubecfg.yaml")

def k0scfg_filename():
    return os.path.join(appdir(), "k0s.yaml")

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
            ["pacman", "-Sy", "--noconfirm", "--needed", "python"]
        ]
    )
    admin_subnet = get_in_config(["admin_subnet"])    
    run_playbook(
        playbook="cluster-node-rpi4-k0s.yml",
        inventory=[node_ip],
        extra_vars={
            "admin_user": get_in_config(["admin_user"]),
            "playbook_user": "root",
            "k0s_binary": get_asset_path("binary_k0s"),
            "ssh_key_file": public_key,
            "k0s_master": node_num == 1,
            "lan_subnet": get_in_config(["cluster", "net", "cidr"]),
            "admin_subnet": admin_subnet,
            "admin_subnet_ssh": calculate_ssh_style_subnet(admin_subnet)
        }
    )

def get_join_tokens(master_node_ip, num_tokens):
    return [str(stdout, encoding="utf8") for stdout, stderr in ssh(
        host=master_node_ip,
        return_stdio=True,
        username="root",
        cmds=[
            ["k0s", "token", "create", "--role", "worker", "--wait"] for x in range(num_tokens)
        ]
    )]

def cluster_init(node_count, master_node, reset):
    worker_nodes = [x for x in range(1, node_count + 1)] # includes master node as well
    master_node_ip = cluster_node_ip(master_node)
    worker_node_ips = [cluster_node_ip(x) for x in worker_nodes]
    print("worker nodes", worker_node_ips)
    if reset:
        print("resetting...")
        for ip in worker_node_ips:
            try:
                ssh(host=ip, username="root", cmds=[
                    ["k0s", "stop"],
                    ["systemctl", "disable", "--now", "k0sworker"],
                    ["k0s", "reset"]
                ])
            except Exception as e:
                print("Error resetting node", ip)
                print(e)
                if not click.confirm("Proceed?"):
                    raise e
    print("configuring control node...")
    ssh(host=master_node_ip, username="root", cmds=[
        ["k0s", "install", "controller", "-c", "/root/k0s.yml"],
        [
            "sed",
            "-ie",
            r'/^\[Service\]/a Environment=ETCD_UNSUPPORTED_ARCH=arm64',
            "/etc/systemd/system/k0scontroller.service"
        ],
        ['systemctl', 'daemon-reload'],
        ["k0s", "start"]
    ])
    tokens = get_join_tokens(master_node_ip, node_count)
    for wip, token in zip(worker_node_ips, tokens):
        print("configuring worker", wip)
        ssh(host=wip, username="root", cmds=[
            ["mkdir", "-p", "/var/lib/k0s"],
            ["bash", "-c", f'echo "{token}" > /var/lib/k0s/join-token'],
            ["k0s", "install", "worker", "--token-file", "/var/lib/k0s/join-token"],
        ])
        if wip == master_node_ip:
            ssh(host=wip, username="root", cmds=[
                ["systemctl", "enable", "--now", "k0sworker"]
            ])
        else:
            ssh(host=wip, username="root", cmds=[
                ["k0s", "start"]
            ])


def cluster_kubecfg():
    master_node_ip = cluster_node_ip(1) # TODO this shouldn't be hardcoded
    kubecfg, _ = ssh(host=master_node_ip, username="root", return_stdio=True, cmds=[
        ["k0s", "kubeconfig", "create", "--groups", "system:masters", "k0s"]
    ])[0]

    filename = kubecfg_filename()
    def opener(path, flags):
        return os.open(path, flags, mode=0o600)
    with open(filename, 'wb', opener=opener) as f:
        f.write(kubecfg)

    # shell(args=["kubectl", "create", "clusterrolebinding", "k0s-admin-binding", "--clusterrole=admin", "--user=k0s", f"--kubeconfig={filename}"])

    print("Run the following (or add it to your bash_profile):")
    print(f'export KUBECONFIG="{filename}"')



def cluster_status():
    raise NotImplementedError()
