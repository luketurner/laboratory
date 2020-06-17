from ...config import get_config
from . import digitalocean_api
from .cluster import create_cluster


def create_node(times=1):
    return _increment_nodes(times)


def delete_node(times=1):
    return _increment_nodes(-times)


def _increment_nodes(count=1):
    config = get_config()["digitalocean"]
    cluster = create_cluster()
    pool = cluster["node_pools"][0]
    pool["count"] += count

    response = digitalocean_api(
        "PUT",
        "/v2/kubernetes/clusters/{}/node_pools/{}".format(cluster["id"], pool["id"]),
        data=pool,
    )
    return response["node_pool"]
