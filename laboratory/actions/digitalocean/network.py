from ...config import get_config, get_lab_name
from . import digitalocean_api


def get_network():
    vpc_name = get_lab_name()
    existing_vpcs = digitalocean_api("GET", "/v2/vpcs")["vpcs"]
    for vpc in existing_vpcs:
        if vpc["name"] == vpc_name:
            return vpc


def create_network():
    vpc_name = get_lab_name()
    config = get_config()["digitalocean"]

    existing_vpc = get_network()
    if existing_vpc:
        return existing_vpc

    response = digitalocean_api(
        "POST",
        "/v2/vpcs",
        data={
            "name": vpc_name,
            "description": "laboratory vpc",
            "region": config["region"],
            "ip_range": config["lab_subnet"],
        },
    )
    return response["vpc"]
