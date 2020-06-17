import click
import requests
import subprocess
import json
import os
import os.path
import inspect
import importlib

from .config import load_config


def _build_actions():
    actions = {}
    base_path = os.path.join(os.path.dirname(__file__), "actions")
    for cloud_name, cloud_path in [
        (x.name, x.path)
        for x in os.scandir(base_path)
        if x.is_dir() and x.name[0] != "_"
    ]:
        # cloud_dir = os.path.join(actions_dir, cloud_name)
        for target_name, target_path in [
            (os.path.splitext(x.name)[0], x.path)
            for x in os.scandir(cloud_path)
            if x.is_file() and x.name[0] != "_"
        ]:
            # for target_file in [x for x in os.listdir(cloud_dir) if x[0] != "_"]:
            # target_name = os.path.splitext(target_file)[0]
            # target_path = os.path.join(cloud_dir, target_file)
            module = importlib.import_module(
                "laboratory.actions.{}.{}".format(
                    cloud_name, inspect.getmodulename(target_path)
                )
            )
            for fn_name, fn in inspect.getmembers(module, inspect.isfunction):
                if fn_name[0] != "_" and target_name in fn_name:
                    action_name = fn_name.split("_")[0]
                    actions[(cloud_name, target_name, action_name)] = {"fn": fn}
    return actions


ACTION_DICT = _build_actions()
CLOUD_SET = set(x for x, y, z in ACTION_DICT.keys())
TARGET_SET = set(y for x, y, z in ACTION_DICT.keys())
ACTION_SET = set(z for x, y, z in ACTION_DICT.keys())


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
        print("{} :: {} {}".format(cloud, action, t))
        action_defn = ACTION_DICT.get(
            (cloud, t, action), ACTION_DICT.get((cloud, "shared", action))
        )
        if not action_defn:
            raise click.ClickException(
                "Unknown action: {} :: {} {}".format(cloud, action, t)
            )
        print(action_defn["fn"]())
