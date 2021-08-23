import click
import os.path
from . import util
from toolz.dicttoolz import assoc_in


from .config import get_config_path, load_config, save_config, set_config_path, config_yaml
from .cluster import prep_node, provision_node, cluster_kubecfg, cluster_status, cluster_init
from .state import set_state_path
from .apis.assets import set_asset_dir

app_dir = util.appdir(create_if_missing=True)
home_dir = util.homedir()

@click.group()
@click.option("--config-file", "-c", type=click.Path(), default=os.path.join(app_dir, "config.yaml"))
@click.option("--state-file", "-s", type=click.Path(), default=os.path.join(app_dir, "state.yaml"))
@click.option("--asset-dir", "-a", type=click.Path(), default=os.path.join(app_dir, "assets"))
def cli(config_file, state_file, asset_dir):
    """Oh yeah!"""
    set_config_path(config_file)
    set_state_path(state_file)
    set_asset_dir(asset_dir)

@cli.command()
@click.option("--admin-user", type=str, prompt="Admin username (e.g. luke)")
@click.option("--admin-subnet", type=str, prompt="Admin subnet CIDR")
@click.option("--admin-private-key", type=click.Path(), default=os.path.join(home_dir, ".ssh", "id_rsa"), prompt="Path to SSH private key to use")
@click.option("--admin-public-key", type=click.Path(), default=os.path.join(home_dir, ".ssh", "id_rsa.pub"), prompt="Path to SSH public key to use")
def configure(admin_user, admin_subnet, admin_public_key, admin_private_key):
    config = load_config()
    config = assoc_in(config, ["admin_user"], admin_user)
    config = assoc_in(config, ["admin_subnet"], admin_subnet)
    config = assoc_in(config, ["admin_public_key"], admin_public_key)
    config = assoc_in(config, ["admin_private_key"], admin_private_key)
    print("Writing config", get_config_path())
    print(config_yaml(config))
    if click.confirm("Accept?"):
        save_config(config)

@cli.group()
def cluster():
    pass


@cluster.command()
@click.option("--cluster-type", type=click.Choice(["lan"]), default="lan", prompt="Cluster type")
@click.option("--net-cidr", type=str, prompt="Subnet CIDR")
@click.option("--router-ip", type=str, prompt="Subnet Router IP")
@click.option("--node-device", type=click.Choice(["rpi4"]), default="rpi4", prompt="Node device type")
@click.option("--node-os", type=click.Choice(["archlinux"]), default="archlinux", prompt="Node OS")
@click.option("--node-arch", type=click.Choice(["aarch64"]), default="aarch64", prompt="Node architecture")
def configure(cluster_type, net_cidr, router_ip, node_device, node_os, node_arch):
    config = load_config()
    config = assoc_in(config, ["cluster", "type"], cluster_type)
    config = assoc_in(config, ["cluster", "net"], {"cidr": net_cidr, "router_ip": router_ip})
    config = assoc_in(config, ["cluster", "node", "device"], node_device)
    config = assoc_in(config, ["cluster", "node", "os"], node_os)
    config = assoc_in(config, ["cluster", "node", "arch"], node_arch)

    print("Writing config", get_config_path())
    print(config_yaml(config))
    if click.confirm("Accept?"):
        save_config(config)


@cluster.group()
def node():
    pass

@node.command()
@click.option("--node-num", "-n", type=int, required=True, prompt="Node number (e.g. 1)")
@click.option("--device", "-d", type=click.Path(readable=False), required=True, prompt="Block device to flash (e.g. /dev/mmcblk0)")
def prep(node_num, device):
    prep_node(
        device=device,
        node_num=node_num
    )

@node.command()
@click.option("--node-num", "-n", type=int, required=True, prompt="Node number (e.g. 1)")
def provision(node_num):
    provision_node(node_num)

@cluster.command()
@click.option("--num-nodes", "-n", type=int, required=True, prompt="Total number of nodes")
@click.option("--master-node", "-m", type=int, required=True, default=1, prompt="Master node")
@click.option("--reset", "-R", type=bool, is_flag=True, default=False)
def init(num_nodes, master_node, reset):
    cluster_init(num_nodes, master_node, reset)

@cluster.command()
def kubecfg():
    cluster_kubecfg()

@cluster.command()
def status():
    cluster_status()
