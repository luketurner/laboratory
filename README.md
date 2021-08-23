# 🧪 Laboratory

This repository has scripts for managing my DevOps "labs":

- The `home` lab has tools for managing the infrastructure in my home (i.e. I own the hardware).
- **DEPRECATED** The `do` lab has tools for managing a "cloud lab" using Digital Ocean.

See **Getting Started** below for installation instructions, then refer to the **Homelab** section.

> **Please note:** this is a personal project, published for reference and inspiration only. 

# Getting Started

Requirements:

- kubectl
- helm
- ansible-playbook
- Arch Linux (for making Arch Linux ARM SD cards)

Getting started:

``` bash
# Clone the repository (installation via pip not currently recommended)
git clone https://github.com/luketurner/laboratory.git
cd laboratory

# install dependencies
poetry install

# Run lab
poetry shell
lab --help
```

# 🏠 Homelab

This section covers using `lab` to manage your homelab.

First, `lab` needs to be configured. Run the following command:

```bash
lab configure
```

Your configuration is saved in `$XDG_CONFIG_DIR/lab/config.yml`.

> **Note:** Currently, `lab` does not manage router configuration for you. Make sure your router's configuration matches what you provided to the `configure` command.

## K8s Cluster

Next, we can initialize the Kubernetes cluster for our home lab. First, we have to run a command to configure the k8s cluster settings:


``` bash
lab cluster configure
```

Once the cluster's configured, we can start adding nodes. 

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

Once you've provisioned all the nodes for the cluster, you can initialize the cluster:

```
lab cluster init
```

# 🌊 Digital Ocean

I'm currently focused on building out my homelab support. A [previous version](https://github.com/luketurner/laboratory/tree/619e0701529c1219a51f8bb83440648c66fee489) of this project had code for setting up a "cloud lab" using Digital Ocean, but this is not currently working or maintained.
