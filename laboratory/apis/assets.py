

import yaml
import os
import os.path

from .http import download_file

_asset_dir = None

# TODO -- move to config
_assets = {
    'archive_archlinuxarm_aarch64': {
        'filename': 'ArchLinuxARM-rpi-aarch64-latest.tar.gz',
        'url': 'http://os.archlinuxarm.org/os/ArchLinuxARM-rpi-aarch64-latest.tar.gz'
    },
    'binary_k0s': {
        'filename': 'k0s',
        'url': 'https://github.com/k0sproject/k0s/releases/download/v1.21.3+k0s.0/k0s-v1.21.3+k0s.0-arm64'
    }
}

def _get_asset(asset_name):
    asset = _assets.get(asset_name)
    if not asset:
        raise Exception("Unknown asset: " + asset_name)
    return asset

def set_asset_dir(p):
    global _asset_dir
    if not os.path.exists(p):
        os.mkdir(p)
    if not os.path.isdir(p):
        raise Exception(f"Not a directory: {p}")
    _asset_dir = p
    return p

def get_asset_dir():
    global _asset_dir
    if not _asset_dir:
        raise Exception("Must call set_asset_dir()")
    return _asset_dir

def get_asset_path(asset_name):
    return os.path.join(get_asset_dir(), _get_asset(asset_name)["filename"])

def get_asset_url(asset_name):
    return _get_asset(asset_name)["url"]

def is_asset_downloaded(asset_name):
    return os.path.exists(get_asset_path(asset_name))

def download_asset(asset_name):
    if not is_asset_downloaded(asset_name):
        print(f"downloading asset: {asset_name}")
        download_file(
            url=get_asset_url(asset_name),
            filename=get_asset_path(asset_name)
        )