import subprocess
import tempfile
import os.path

from ...apis.kubecfg import kubectl, kubecfg
from ...apis.shell import shell
from ...config import get_lab_name


def create_cert_operator():

    kubectl("vendor/cert-manager.yaml")

    with tempfile.TemporaryDirectory() as tempdir:
        key_path = os.path.join(tempdir, "ca.key")
        cert_path = os.path.join(tempdir, "ca.crt")

        shell(["openssl", "genrsa", "-out", key_path, "4096"])
        shell(
            [
                "openssl",
                "req",
                "-x509",
                "-new",
                "-nodes",
                "-key",
                key_path,
                "-subj",
                "/CN={}".format(get_lab_name()),
                "-days",
                "3650",
                "-reqexts",
                "v3_req",
                "-extensions",
                "v3_ca",
                "-out",
                cert_path,
            ]
        )

        with open(key_path, "r") as keyfile:
            with open(cert_path, "r") as certfile:
                kubecfg(
                    "cluster-ca.jsonnet", {"key": keyfile.read(), "cert": certfile.read(),},
                )
