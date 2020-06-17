from ...config import get_config, get_lab_name
from . import digitalocean_api
from .network import get_network


def get_cluster():
  cluster_name = get_lab_name()
  existing_clusters = digitalocean_api("GET", "/v2/kubernetes/clusters")["kubernetes_clusters"]
  for cluster in existing_clusters:
    if cluster['name'] == cluster_name:
      return cluster


def create_cluster():
  config = get_config()['digitalocean']
  cluster_name = get_lab_name()

  existing_cluster = get_cluster()
  if existing_cluster:
    return existing_cluster

  vpc = get_network()

  response = digitalocean_api("POST", "/v2/kubernetes/clusters", data={
    "name": cluster_name,
    "region": config["region"],
    "version": config["k8s_version"],
    "auto_upgrade": config["k8s_auto_upgrade"],
    "tags": [], # TODO -- tags?
    "node_pools": [{
      "size": config["node_droplet_size"],
      "name": cluster_name + "-nodes",
      "count": 0
    }],
    "vpc": vpc['id']
  })
  return response["kubernetes_cluster"]

def options_cluster():
  return digitalocean_api("GET", "/v2/kubernetes/options")