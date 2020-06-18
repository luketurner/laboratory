import subprocess
import tempfile
import os.path

from ...apis.kubecfg import kubecfg
from ...apis.digitalocean import digitalocean_api
from ...config import get_lab_name
from .network import get_network


def create_ingress_operator():
    kubecfg("vendor/routegroup.yaml")
    kubecfg("ingress-operator-cloud.jsonnet")
    # TODO add certificates to created load balancer


def get_ingress_operator():
    vpc = get_network()
    for lb in digitalocean_api("GET", "/v2/load_balancers")["load_balancers"]:
        if lb["vpc_uuid"] == vpc["id"]:
            return lb
