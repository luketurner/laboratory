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
            ["k0s", "token", "create", "--role", "worker"] for x in range(num_tokens)
        ]
    )]

def cluster_init(node_count, master_node, reset):
    download_asset('binary_k0s')
    download_asset('binary_k0sctl')
    k0sctl = get_asset_path('binary_k0sctl')
    k0scfg = k0scfg_filename()
    result = shell(
        [k0sctl, "init", "--k0s"],
        capture_output=True
    )
    data = yaml.load(result.stdout)
    data["spec"]["hosts"] = [{
        "role": "controller+worker" if n == 1 else "worker",
        "ssh": {
            "address": cluster_node_ip(n),
            "keyPath": get_in_config(["admin_private_key"]),
            "port": 22,
            "user": "root"
        },
        "k0sBinaryPath": get_asset_path("binary_k0s")
    } for n in range(1, node_count + 1)]
    data["spec"]["k0s"]["config"]["spec"]["telemetry"] = {"enabled": False}
    string_data = yaml.dump(data)
    print("Writing", k0scfg)
    print(string_data)
    if not click.confirm("Apply?"):
        return
    with open(k0scfg, "w") as f:
        f.write(string_data)
    shell([k0sctl, "apply", "--debug", "--config", k0scfg])

    



def cluster_init2(node_count, master_node, reset):
    worker_nodes = [x for x in range(1, node_count + 1) if x != master_node]
    master_node_ip = cluster_node_ip(master_node)
    worker_node_ips = [cluster_node_ip(x) for x in worker_nodes]
    if reset:
        ssh(host=master_node_ip, username="root", cmds=[
            ["k0s", "stop"],
            ["k0s", "reset"]
        ])
    ssh(host=master_node_ip, username="root", cmds=[
        ["k0s", "install", "controller", "-c", "/root/k0s.yml"],
        [
            "sed",
            "-ie",
            r'/^\[Service\]/a Environment=ETCD_UNSUPPORTED_ARCH=arm64',
            "/etc/systemd/system/k0scontroller.service"
        ],
        ["systemctl", "enable", "--now", "k0scontroller"]
    ])
    tokens = get_join_tokens(master_node_ip, node_count - 1)
    for wip, token in zip(worker_node_ips, tokens):
        if reset:
            ssh(host=wip, username="root", cmds=[
                ["k0s", "stop"],
                ["k0s", "reset"]
            ])
        ssh(host=wip, username="root", cmds=[
            ["mkdir", "-p", "/var/lib/k0s"],
            ["bash", "-c", f'echo "{token}" > /var/lib/k0s/join-token'],
            ["k0s", "install", "worker", "--token-file", "/var/lib/k0s/join-token"],
            ["k0s", "enable"]
        ])


def cluster_kubecfg():
    master_node_ip = cluster_node_ip(1) # TODO this shouldn't be hardcoded
    kubecfg, _ = ssh(host=master_node_ip, username="root", return_stdio=True, cmds=[
        ["k0s", "kubeconfig", "create", "--groups", "system:masters", "k0s"]
    ])[0]

    filename = kubecfg_filename()
    with open(filename, 'wb') as f:
        f.write(kubecfg)

    # shell(args=["kubectl", "create", "clusterrolebinding", "k0s-admin-binding", "--clusterrole=admin", "--user=k0s", f"--kubeconfig={filename}"])

    print("Run the following (or add it to your bash_profile):")
    print(f'export KUBECONFIG="{filename}"')



def cluster_status():
    raise NotImplementedError()
