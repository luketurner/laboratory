import subprocess
import tempfile
import os.path

from ...apis.kubecfg import kubecfg
from ...apis.shell import shell
from ...apis.digitalocean import digitalocean_api
from ...config import get_lab_name
from .network import get_network


def create_ingress_operator():
    lab_name = get_lab_name()
    kubecfg("vendor/routegroup.yaml")
    kubecfg("ingress-operator-cloud.jsonnet")


    lb = get_ingress_operator()

    for rule in lb['forwarding_rules']:
        if rule["entry_protocol"] == "https":
            # Already have HTTPS configured, we're done!
            return lb

    for cert in digitalocean_api("GET", "/v2/certificates")["certificates"]:
        if cert["name"] == lab_name + "-ingress":
            certificate = cert

    if not certificate:
        certificate = _add_cert(lab_name)

        
    lb["redirect_http_to_https"] = True
    lb["forwarding_rules"].append({
        "entry_protocol": "https",
        "entry_port": 443,
        "target_protocol": "http",
        "target_port": lb["forwarding_rules"][0]["target_port"],
        "tls_passthrough": False,
        "certificate_id": certificate["id"]
    })
    lb["region"] = lb["region"]["slug"]
    lb = digitalocean_api("PUT", "/v2/load_balancers/{}".format(lb["id"]), data=lb)["load_balancer"]

    return lb




def get_ingress_operator():
    vpc = get_network()
    for lb in digitalocean_api("GET", "/v2/load_balancers")["load_balancers"]:
        if lb["vpc_uuid"] == vpc["id"]:
            return lb


def _add_cert(lab_name):
    # TODO the following adds a self-signed cert to the Load Balancer. We should use Let's Encrypt instead.
    with tempfile.TemporaryDirectory() as tempdir:
        key_path = os.path.join(tempdir, "key.pem")
        cert_path = os.path.join(tempdir, "cert.pem")

        shell([
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-keyout", key_path, "-out", cert_path, "-days", "1", 
            "-subj", "/CN=Test", "-nodes"
        ])

        with open(key_path, "r") as key:
            with open(cert_path, "r") as cert:
                certificate = digitalocean_api("POST", "/v2/certificates", data={
                    "name": lab_name + "-ingress",
                    "type": "custom",
                    "private_key": key.read(),
                    "leaf_certificate": cert.read()
                })["certificate"]
