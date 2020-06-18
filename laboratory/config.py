import os.path
import configparser

import click

_config = None


def _prefixed(path, file_prefix):
    return os.path.join(os.path.dirname(path), file_prefix + os.path.basename(path))


def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    config.read(_prefixed(config_file, "secret-"))

    context = click.get_current_context()
    context.ensure_object(dict)
    context.obj["config"] = config
    context.obj["config_file"] = config_file

    return config


def get_config():
    return click.get_current_context().obj["config"]


def get_config_file():
    return click.get_current_context().obj["config_file"]


def get_lab_name():
    return click.get_current_context().obj["config"]["laboratory"]["lab_name"]


def get_digitalocean_config():
    return get_config()["digitalocean"]


def get_cloud():
    cloud = click.get_current_context().obj.get("cloud") or get_config()[
        "laboratory"
    ].get("default_cloud")
    if not cloud:
        raise AppException("Missing required config field: laboratory.default_cloud")
    return cloud


def get_manifest_directory():
    config_dir = os.path.dirname(get_config_file())
    manifest_dir = get_config()["laboratory"].get("manifest_directory")
    if not manifest_dir:
        raise AppException(
            "Missing required config field: laboratory.manifest_directory"
        )
    if not os.path.isabs(manifest_dir):
        manifest_dir = os.path.join(config_dir, manifest_dir)
    return os.path.normpath(manifest_dir)
