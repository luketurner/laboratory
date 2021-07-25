

import yaml
import os
import os.path

_state_cache = {}
_state_path = None

def set_state_path(p):
    global _state_path
    _state_path = p
    return p

def get_state_path():
    global _state_path
    if not _state_path:
        raise Exception("Must call set_state_path()")
    return _state_path

def _load_state(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return yaml.safe_load(f)

def _load_state_cached():
    global _state_cache
    path = get_state_path()
    cached = _state_cache.get(path)
    if cached:
        return cached
    state = _load_state(path)
    _state_cache[path] = state
    return state

def load_state():
    return _load_state_cached()

def save_state(state):
    with open(get_state_path(), "w") as f:
        yaml.dump(state, f)

def state_yaml(state):
    return yaml.dump(state)
