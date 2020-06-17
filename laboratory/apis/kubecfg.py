import subprocess
import os.path
from .. import AppException
from ..config import get_manifest_directory
from .shell import shell

def kubecfg(manifest, args=None):
  manifest_path = os.path.normpath(os.path.join(get_manifest_directory(), manifest))
  cmd = ["kubecfg", "update", manifest_path]
  for k, v in (args or {}).items():
    cmd += ["--tla-str", k+"="+v]
  return shell(cmd)


def kubectl(manifest):
  manifest_path = os.path.normpath(os.path.join(get_manifest_directory(), manifest))
  return shell(["kubectl", "apply", "-f", manifest_path])