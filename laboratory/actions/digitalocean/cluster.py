import os

from ... import AppException
from ...config import get_digitalocean_config, get_lab_name
from ...apis.digitalocean import digitalocean_api
from .network import get_network


def get_cluster():
    cluster_name = get_lab_name()
    existing_clusters = digitalocean_api("GET", "/v2/kubernetes/clusters")["kubernetes_clusters"]
    for cluster in existing_clusters:
        if cluster["name"] == cluster_name:
            return cluster


def connect_cluster(expiry=0):

    existing_cluster = get_cluster()

    if not existing_cluster:
        raise AppException("Cannot find cluster to connect; try 'lab create cluster' first")

    return digitalocean_api(
        "GET", "/v2/kubernetes/clusters/{}/kubeconfig".format(existing_cluster["id"]), query={"expiry": expiry},
    )


def create_cluster():
    config = get_digitalocean_config()
    cluster_name = get_lab_name()

    existing_cluster = get_cluster()
    if existing_cluster:
        return existing_cluster

    vpc = get_network()
    if not vpc:
        raise AppException("Cannot create cluster: vpc {} not found".format(cluster_name))

    response = digitalocean_api(
        "POST",
        "/v2/kubernetes/clusters",
        data={
            "name": cluster_name,
            "region": config["region"],
            "version": config["k8s_version"],
            "auto_upgrade": config.getboolean("k8s_auto_upgrade"),
            # "tags": [], # TODO
            # "maintenance_policy": {}, # TODO
            "node_pools": [{"size": config["node_droplet_size"], "name": cluster_name + "-nodes", "count": 1,}],
            "vpc_uuid": vpc["id"],
        },
    )
    return response["kubernetes_cluster"]


def options_cluster():
    return digitalocean_api("GET", "/v2/kubernetes/options")
