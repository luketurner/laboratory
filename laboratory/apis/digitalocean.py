import requests

from ..config import get_digitalocean_config
from .. import AppException


def digitalocean_api(method, path, data=None, query=None):
    api_key = get_digitalocean_config().get("api_key")
    response = requests.request(
        method,
        "https://api.digitalocean.com" + path,
        headers={"Authorization": "Bearer " + api_key},
        json=data,
        params=query,
    )
    if response.status_code >= 400:
        raise AppException("{} {} response: {} {}".format(method, path, response.status_code, response.json()))
    return response.json() if "json" in response.headers["content-type"] else response.text
