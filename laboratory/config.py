

import yaml
import os
import os.path

from toolz.dicttoolz import get_in

_config_cache = {}
_config_path = None

def set_config_path(p):
    global _config_path
    _config_path = p
    return p

def get_config_path():
    global _config_path
    if not _config_path:
        raise Exception("Must call set_config_path()")
    return _config_path

def _load_config(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f)

def _load_config_cached():
    global _config_cache
    path = get_config_path()
    cached = _config_cache.get(path)
    if cached:
        return cached
    config = _load_config(path)
    _config_cache[path] = config
    return config

def load_config():
    return _load_config_cached()

def save_config(config):
    with open(get_config_path(), "w") as f:
        yaml.dump(config, f)

def config_yaml(config):
    return yaml.dump(config)

def get_in_config(keys):
    return get_in(keys, load_config())