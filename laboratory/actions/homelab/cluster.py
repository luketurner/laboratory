import os

from ... import AppException
from ...config import get_digitalocean_config, get_lab_name
from ...apis.digitalocean import digitalocean_api
from .network import get_network


def get_cluster():
    cluster_name = get_lab_name()
    


def connect_cluster(expiry=0):

    existing_cluster = get_cluster()

    if not existing_cluster:
        raise AppException("Cannot find cluster to connect; try 'lab create cluster' first")

    return digitalocean_api(
        "GET", "/v2/kubernetes/clusters/{}/kubeconfig".format(existing_cluster["id"]), query={"expiry": expiry},
    )


def create_cluster():
    cluster_name = get_lab_name()

    existing_cluster = get_cluster()
    if existing_cluster:
        return existing_cluster
