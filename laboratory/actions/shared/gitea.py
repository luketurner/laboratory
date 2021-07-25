import subprocess
import tempfile
import os.path
import secrets
import time

from ...apis.kubecfg import kubecfg, kubeshell
from ...config import get_lab_name, get_dns_name, get_user_name, get_user_email


def create_gitea():

    admin_user = get_user_name()
    admin_email = get_user_email()
    admin_password = secrets.token_urlsafe(32)
    secret_key = secrets.token_urlsafe(32)
    dns_name = get_dns_name("gitea")

    kubecfg("gitea.jsonnet", {
      "secretKey": secret_key,
      "dnsName": dns_name
    })

    # Wait for Gitea pod to be live before we try to run admin commands on it
    time.sleep(10) # TODO - better way to wait for Gitea readiness


    try:
      kubeshell("deployment/gitea", [
        "gitea", "admin", "create-user",
        "--username", admin_user,
        "--password", admin_password,
        "--email", admin_email,
        "--admin", "true",
      ])
    except Exception as e:
      # Hopefully, this error was because the user already exists.
      # TODO - Do we want to parse the stderr output to check?
      pass

    return {
      "username": admin_user,
      "password": admin_password,
      "secret_key": secret_key,
      "dns_name": dns_name,
      "user_email": admin_email,
    }