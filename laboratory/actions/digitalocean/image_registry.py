from ...config import get_digitalocean_config, get_lab_name
from ...apis.digitalocean import digitalocean_api


def get_image_registry():
    return digitalocean_api("GET", "/v2/registry")["registry"]


def create_image_registry():
    registry_name = get_lab_name()

    registry = get_image_registry()
    if registry:
        return registry

    response = digitalocean_api(
        "POST",
        "/v2/refistry",
        data={
            "name": registry_name,
        },
    )
    return response["registry"]

def connect_image_registry():
  return digitalocean_api("GET", "/v2/registry/docker-credentials", query={ "read_write": "true" })
