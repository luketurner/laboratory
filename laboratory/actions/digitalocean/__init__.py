import requests

from ...config import get_config


def digitalocean_api(method, path, data=None, query=None):
    api_key = get_config()["digitalocean"].get("api_key")
    return requests.request(
        method,
        "https://api.digitalocean.com" + path,
        headers={"Authorization": "Bearer " + api_key},
        json=data,
        params=query,
    ).json()
