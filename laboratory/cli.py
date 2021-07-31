import click
import os.path
from . import util
from toolz.dicttoolz import assoc_in


from .config import get_config_path, load_config, save_config, set_config_path, config_yaml
from .cluster import prep_node, provision_node, cluster_kubecfg, cluster_status
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
def configure(admin_user):
    config = load_config()
    config = assoc_in(config, ["admin_user"], admin_user)
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
@click.option("--public-key", "-p", type=click.Path(), default=os.path.join(home_dir, ".ssh", "id_rsa.pub"), prompt="SSH public key file")
@click.option("--node-num", "-n", type=int, required=True, prompt="Node number (e.g. 1)")
@click.option("--device", "-d", type=click.Path(readable=False), required=True, prompt="Block device to flash (e.g. /dev/mmcblk0)")
def prep(public_key, node_num, device):
    prep_node(
        device=device,
        public_key=public_key,
        node_num=node_num
    )

@node.command()
@click.option("--public-key", "-p", type=click.Path(), default=os.path.join(home_dir, ".ssh", "id_rsa.pub"), prompt="SSH public key file")
@click.option("--node-num", "-n", type=int, required=True, prompt="Node number (e.g. 1)")
def provision(node_num, public_key):
    provision_node(node_num, public_key)

@cluster.command()
def kubecfg():
    cluster_kubecfg()

@cluster.command()
def status():
    cluster_status()
