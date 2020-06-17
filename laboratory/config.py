import os.path
import configparser

import click

_config = None

def _prefixed(path, file_prefix):
  return os.path.join(os.path.dirname(path), file_prefix + os.path.basename(path))

def load_config(config_file):
  config = configparser.ConfigParser()
  config.read(config_file)
  config.read(_prefixed(config_file, 'secret-'))

  context = click.get_current_context()
  context.ensure_object(dict)
  context.obj['config'] = config

  return config

def get_config():
  return click.get_current_context().obj['config']

def get_lab_name():
  return click.get_current_context().obj['config']['laboratory']['lab_name']

def get_cloud():
  cloud = click.get_current_context().obj.get('cloud') or get_config()["laboratory"].get("default_cloud")
  if not cloud:
    raise Exception("Must specify a cloud to use.")