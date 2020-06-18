import subprocess
import os.path
import tempfile
import contextlib

from .. import AppException
from ..config import get_manifest_directory, get_cloud
from .shell import shell


def kubecfg(manifest, args=None):
  manifest_path = os.path.normpath(os.path.join(get_manifest_directory(), manifest))
  with kubeconfig() as kc:
    cmd = ["kubecfg", "--kubeconfig", kc, "update", manifest_path]
    for k, v in (args or {}).items():
      cmd += ["--tla-str", k+"="+v]
    return shell(cmd)


def kubectl(manifest):
  manifest_path = os.path.normpath(os.path.join(get_manifest_directory(), manifest))
  with kubeconfig() as kc:
    return shell(["kubectl", "--kubeconfig", kc,  "apply", "-f", manifest_path])

@contextlib.contextmanager
def kubeconfig():
  cloud = get_cloud()

  with tempfile.NamedTemporaryFile('w') as f:
    # TODO -- abstract this better -- should not require hardcoded cloud type check
    if cloud == "digitalocean":
      from laboratory.actions.digitalocean.cluster import connect_cluster
      f.write(connect_cluster())
      f.flush()
      yield f.name
    else:
      raise AppException("Cannot get kubeconfig for cloud: {}".format(cloud))
