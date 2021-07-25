import click
import os.path
from . import util
from toolz.dicttoolz import assoc_in


from .config import get_config_path, load_config, save_config, set_config_path, config_yaml
from .cluster import prep_node, provision_node, cluster_kubecfg, cluster_status
from .state import set_state_path

app_dir = util.appdir(create_if_missing=True)

@click.group()
@click.option("--config-file", "-c", type=click.Path(), default=os.path.join(app_dir, "config.yaml"))
@click.option("--state-file", "-s", type=click.Path(), default=os.path.join(app_dir, "state.yaml"))
def cli(config_file, state_file):
    """Oh yeah!"""
    set_config_path(config_file)
    set_state_path(state_file)

@cli.command()
def init():
    print("Resetting config file:", get_config_path())
    print("This will DELETE existing data.")
    if click.confirm("Continue?"):
        save_config({})

@cli.group()
def cluster():
    pass


@cluster.command()
def init():
    config = load_config()
    print("Gathering config info...")
    print("(Note: many prompts just have one option for now.)")
    config = assoc_in(config, ["cluster", "type"], click.prompt("Cluster type", type=click.Choice(['lan'])))
    config = assoc_in(config, ["cluster", "net"], {
        "cidr": click.prompt("[network] Subnet CIDR block:", type=str),
        "router_ip": click.prompt("[network] Router IP:", type=str)
    })
    config = assoc_in(config, ["cluster", "node", "device"], click.prompt("Node device type", type=click.Choice(['rpi4'])))
    config = assoc_in(config, ["cluster", "node", "os"], click.prompt("Node OS", type=click.Choice(['archlinux'])))
    config = assoc_in(config, ["cluster", "node", "arch"], click.prompt("Node architecture", type=click.Choice(['aarch64'])))

    print("Writing config", get_config_path())
    print(config_yaml(config))
    if click.confirm("Accept?"):
        save_config(config)


@cluster.group()
def node():
    pass

@node.command()
def prep():
    prep_node()

@node.command()
def provision():
    provision_node()

@cluster.command()
def kubecfg():
    cluster_kubecfg()

@cluster.command()
def status():
    cluster_status()
