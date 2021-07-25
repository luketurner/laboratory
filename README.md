# Laboratory

This repository has scripts for managing my DevOps "labs":

- The `home` lab has tools for managing the infrastructure in my home (i.e. I own the hardware).
- **DEPRECATED** The `do` lab has tools for managing a "cloud lab" using Digital Ocean.

See **Getting Started** below for installation instructions, then refer to **Usage (Homelab)** for details on
how to use `lab` to manage your homelab.

> Please note: this is a personal project, published for reference and inspiration only.

# Getting Started

``` bash
# Clone the repository (installation via pip not currently recommended)
git clone https://github.com/luketurner/laboratory.git
cd laboratory

# install dependencies
poetry install

# Run lab
poetry run lab --help
```

# Usage (Homelab)

First, we can initialize the `home` lab:

``` bash
lab -l home init
```

The `init` command doesn't actually make any infra changes -- it just adds the `home` lab to your `config.yaml` so we can do operations on it. You'll be prompted for required lab-wide configuration like the subnet CIDR block and router IP.

> **Note:** Currently, `lab` does not manage home router configuration for you. Make sure your router's configuration matches what you provided to the `init` command.

Since `home` is the default value for the `--lab/-l` flag, it will be omitted from future examples, like so:

``` bash
lab init
```

## K8s Cluster

Next, we can initialize the Kubernetes cluster for our home lab. (This is also a configuration-only command.)

``` bash
lab cluster init
```

Once the cluster's initialized, we have all the configuration we need to start provisioning nodes.

> **Note:** There's a lot of assumptions baked in here about how my homelab works. A few important ones:
>
> - Nodes are Raspberry Pi 4s running Arch Linux ARM (aarch64)
> - Nodes use static IP configuration
> - The cluster uses `k0s` instead of standard `k8s`
> - All persistent storage is farmed out to a NAS (Not configured in this step)

Adding a node has two steps:

1. Prep
2. Provisioning

The prep step covers everything needed to get the node "up" on the network, such that you can connect to it over SSH. This includes plugging the Pi into a switch, installing an OS on the SD card, etc.

```
lab cluster node prep
```

The provisioning step covers the rest of the process of running updates, installing software, etc. and is handled by running Ansible playbooks once SSH access is available.

```
lab cluster node provision
```