from .apis.ansible import run_playbook
from .apis.script import script
from .apis.assets import download_asset, get_asset_path

def prep_node(node_num, device, public_key):
    download_asset('archive_archlinuxarm_aarch64')
    script('mksdcard.sh', [
        '--node', str(node_num),
        '--device', device,
        '--public-key', public_key,
        '--archive', get_asset_path('archive_archlinuxarm_aarch64')
    ], sudo=True)

def provision_node():
    run_playbook(playbook="foobar.yaml", inventory=[], extra_vars={})

def cluster_status():
    raise NotImplementedError()

def cluster_kubecfg():
    raise NotImplementedError()
