import click
import requests
import subprocess
import json

import os
import os.path
import configparser

CLOUDS = ['digitalocean', 'home']
TARGETS = ['cluster', 'node']

def prefixed(path, file_prefix):
  return os.path.join(os.path.dirname(path), file_prefix + os.path.basename(path))

def load_config(config_file):
  config = configparser.ConfigParser()
  config.read(config_file)
  config.read(prefixed(config_file, 'secret-'))
  return config

def get_config():
  return click.get_current_context().obj['config']

def get_lab_name():
  return click.get_current_context().obj['config']['laboratory']['lab_name']

def get_cloud():
  cloud = click.get_current_context().obj.get('cloud') or get_config()["laboratory"].get("default_cloud")
  if not cloud:
    raise Exception("Must specify a cloud to use.")


@click.group()
@click.option("--cloud", "-C", type=click.Choice(CLOUDS), default=None)
@click.option("--config", "-c", type=click.Path(), default="config.ini")
def cli(cloud, config):
  config_data = load_config(config)
  ctx = click.get_current_context()
  ctx.ensure_object(dict)
  ctx.obj['config'] = config_data
  ctx.obj['cloud'] = cloud


@cli.command()
@click.argument("TARGET", type=click.Choice(TARGETS), required=True)
def create(target):
  cloud = get_cloud()
  if cloud == "digitalocean":
    if target == "cluster":
      return create_digitalocean_cluster()
    if target == "node":
      return update_digitalocean_cluster_node(1)
  raise NotImplementedError("{}-{}".format(cloud, target))
  


def create_digitalocean_vpc():
  vpc_name = get_lab_name()
  config = get_config()['digitalocean']
  existing_vpcs = digitalocean_api("GET", "/v2/vpcs")["vpcs"]
  for vpc in existing_vpcs:
    if vpc.name == vpc_name:
      return vpc
  response = digitalocean_api("POST", "/v2/vpcs", data={
    "name": cluster_name,
    "description": "laboratory vpc",
    "region": config["region"],
    "ip_range": config["lab_subnet"]
  })
  return response['vpc']


def create_digitalocean_cluster():
  config = get_config()['digitalocean']
  cluster_name = get_lab_name()

  existing_clusters = digitalocean_api("GET", "/v2/kubernetes/clusters")["kubernetes_clusters"]
  for cluster in existing_clusters:
    if cluster.name == cluster_name:
      return cluster

  vpc = create_digitalocean_vpc()

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


def update_digitalocean_cluster_node(count=1):
  config = get_config()['digitalocean']
  cluster = create_digitalocean_cluster()
  pool = cluster['node_pools'][0]
  pool['count'] += count

  response = digitalocean_api("PUT", "/v2/kubernetes/clusters/{}/node_pools/{}".format(cluster['id'], pool['id']), data=pool)
  return response['node_pool']


def digitalocean_api(method, path, data=None, query=None):
  api_key = get_config()["digitalocean"].get("api_key")
  return requests.request(method, 
    "https://api.digitalocean.com/v2/" + path, 
    headers={"Authorization": "Bearer "+api_key},
    json=data,
    params=query
  ).json()