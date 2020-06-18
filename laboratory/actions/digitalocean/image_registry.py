import json

from ...config import get_digitalocean_config, get_lab_name
from ...apis.digitalocean import digitalocean_api
from ...apis.kubecfg import kubecfg

def get_image_registry():
    return digitalocean_api("GET", "/v2/registry")["registry"]


def create_image_registry():
    registry_name = get_lab_name()

    registry = get_image_registry()
    if not registry:
        registry = digitalocean_api("POST", "/v2/registry", data={"name": registry_name})["registry"]

    read_config = digitalocean_api("GET", "/v2/registry/docker-credentials")
    write_config = digitalocean_api("GET", "/v2/registry/docker-credentials", query={ "read_write": "true" })
    
    kubecfg("image-registry-cloud.jsonnet", {
        "dockerconfigjson": json.dumps(read_config),
        "dockerconfigjson_write": json.dumps(write_config)
    })

    return registry


def connect_image_registry():
    return digitalocean_api(
        "GET", "/v2/registry/docker-credentials", query={"read_write": "true"}
    )
