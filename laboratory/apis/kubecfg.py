import subprocess
import os.path
from .. import AppException
from ..config import get_manifest_directory

def kubecfg(manifest, args=None):
  manifest_directory = get_manifest_directory()
  manifest_path = os.path.normpath(os.path.join(manifest_directory, manifest))
  cmd = ["kubecfg", "update", manifest_path]
  for k, v in (args or {}).items():
    cmd += ["--tla-str", k+"="+v]
  exit_code = subprocess.call(cmd)
  if exit_code > 0:
    raise AppException("kubecfg returned exit code: {}".format(exit_code))
  return exit_code