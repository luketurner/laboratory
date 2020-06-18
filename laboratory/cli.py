import click
import requests
import subprocess
import json
import os
import os.path
import inspect
import importlib

from .config import load_config

def _action_functions(cloud, target):
    module = importlib.import_module("laboratory.actions.{}.{}".format(cloud.replace("-", "_"), target.replace("-", "_")))
    for fn_name, fn in inspect.getmembers(module, inspect.isfunction):
        if fn_name[0] != "_" and target.replace("-", "_") in fn_name:
            yield fn_name.split("_")[0], fn

def _target_files(base_path):
    for f in os.scandir(base_path):
        if f.is_file() and f.name[0] != "_":
            yield os.path.splitext(f.name)[0].replace("_", "-"), f.path

def _cloud_dirs(base_path):
    for f in os.scandir(base_path):
        if f.is_dir() and f.name[0] != "_":
            yield f.name.replace("_", "-"), f.path



def _build_actions():
    action_dict = {}
    actions = set()
    clouds = set()
    targets = set()

    def add_action(cloud, action, target, fn):
        key = (cloud, action, target)
        if key not in action_dict:
            action_dict[key] = { "fn": fn }

    base_path = os.path.join(os.path.dirname(__file__), "actions")
    for cloud_name, cloud_path in _cloud_dirs(base_path):
        clouds.add(cloud_name)
        for target_name, target_path in _target_files(cloud_path):
            targets.add(target_name)
            for action_name, action_fn in _action_functions(cloud_name, target_name):
                actions.add(action_name)
                add_action(cloud_name, action_name, target_name, action_fn)

    clouds.remove("shared")

    return action_dict, clouds, actions, targets

ACTION_DICT, CLOUD_SET, ACTION_SET, TARGET_SET = _build_actions()

@click.command()
@click.option("--cloud", "-C", type=click.Choice(CLOUD_SET), default=None)
@click.option("--config-path", "-c", type=click.Path(), default="config.ini")
@click.option("--dry-run", "-d", is_flag=True)
@click.argument("action", type=click.Choice(ACTION_SET), required=True)
@click.argument("target", type=click.Choice(TARGET_SET), required=True, nargs=-1)
def cli(cloud, config_path, dry_run, action, target):
    """Oh yeah!"""
    config = load_config(config_path)
    cloud = cloud or config["laboratory"]["default_cloud"]
    config["laboratory"]["cloud"] = cloud
    for t in target:
        action_defn = ACTION_DICT.get(
            (cloud, action, t), ACTION_DICT.get(("shared", action, t))
        )
        if not action_defn:
            print("Supported actions:", "\n".join(" ".join(x) for x in ACTION_DICT.keys()), sep="\n")
            raise click.ClickException(
                "Unknown action: {} :: {} {}".format(cloud, action, t)
            )
        result = action_defn["fn"]()
        print(result if isinstance(result, str) else json.dumps(result))
