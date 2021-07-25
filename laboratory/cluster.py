from .apis.ansible import run_playbook
from .apis.script import script

def prep_node():
    script('mksdcard.sh', [])

def provision_node():
    run_playbook(playbook="foobar.yaml", inventory=[], extra_vars={})

def cluster_status():
    raise NotImplementedError()

def cluster_kubecfg():
    raise NotImplementedError()
