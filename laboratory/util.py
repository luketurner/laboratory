import os
import os.path

def appdir(create_if_missing=False):
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.environ.get("HOME"), ".config")
    app_dir = os.path.join(xdg_config_home, "lab")
    if create_if_missing:
        os.makedirs(app_dir, exist_ok=True)
    return app_dir
