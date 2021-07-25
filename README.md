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

The provisioning step covers the rest of the process of running updates, installing software, etc. and is handled by running Ansible playbooks once SSH access is available.

Once prep+provisioning is finished, the node should be fully "added" to the cluster. No further manual maintenance is required.

For each node, run:

``` bash
# N.B. MAKE SURE THE -d FLAG IS YOUR SDCARD BLOCK DEVICE
# OR YOU COULD LOSE DATA WITH THIS COMMAND
lab node prep -n 1 -d /dev/sdb

# Once the node is prepped and available over SSH
lab node provision -n 1
```

The `-n 1` indicates this is the first node. Subsequent nodes should use `-n 2`, `-n 3` etc.




# Old

When it comes to DevOps, I believe you don't _understand_ it unless you can _automate_ it. So, laboratory operations are entirely wrapped up in a repeatable, idempotent CLI called `lab`.

> **Warning:** Like my laboratory itself, this CLI is a _personal project_. A core purpose of the project is _learning_. I've provided it as reference and inspiration, not as a polished software product you should use.

# Quick Reference

A laboratory consists of **clouds**. A "cloud" is an independent cluster, which may be running literally in the cloud (e.g. on DigitalOcean) or it may be running in your home network. A single laboratory can have multiple clouds, but only a single instance of each type of cloud.

Within the clouds, laboratory functions and apparatus are broken into semi-independent units called **features**. Splitting things into features make it easier to deploy the cloud piecemeal for learning purposes, and to opt-in or opt-out of different behaviors.

```
┌───────────────────────────────────────────────────────┐
│Laboratory                                             │
│┌─────────────────────────────────────────────────────┐│
││Cloud                                                ││
││┌──────────────┐ ┌──────────────┐ ┌──────────────┐   ││
│││   Feature    │ │   Feature    │ │   Feature    │...││
│││              │ │              │ │              │   ││
││└──────────────┘ └──────────────┘ └──────────────┘   ││
│└─────────────────────────────────────────────────────┘│
│┌─────────────────────────────────────────────────────┐│
││Cloud                                                ││
││┌──────────────┐ ┌──────────────┐ ┌──────────────┐   ││
│││   Feature    │ │   Feature    │ │   Feature    │...││
│││              │ │              │ │              │   ││
││└──────────────┘ └──────────────┘ └──────────────┘   ││
│└─────────────────────────────────────────────────────┘│
│                          ...                          │
└───────────────────────────────────────────────────────┘
```

Laboratory operations are performed with the `lab` CLI. Each feature has a supported set of operations, called **actions**. For example:

```bash
# run "create" action on "cluster" feature in the "digitalocean" cloud
lab -C digitalocean create cluster
```

The following table indicates which **features** and **actions** are supported or planned for each type of **cloud**. Pairs of emoji are used to indicate status: the left emoji indicates the cloud, and the right emoji indicates the status for that cloud.

- Clouds: :ocean: Digital Ocean (managed) - :house: Pi Homelab
- Statuses: :x: N/A - :ghost: Planned, not started - :mortar_board: Learning/Planning - :heavy_check_mark: Finished 

| Feature name | Verbs | Status | Notes
|-|-|-|-|
| network           | get, create           | :ocean::heavy_check_mark: / :house::ghost: | Singleton network (VPC)
| cluster           | get, create, options, connect  | :ocean::heavy_check_mark: / :house::ghost: | Singleton Kubernetes cluster
| node              | create, delete        | :ocean::heavy_check_mark: / :house::ghost: | Manage nodes in the cluster
| storage-operator  | create                | :ocean::heavy_check_mark: / :house::ghost: | Handles PVCs by allocating block storage
| cert-operator     | create                | :ocean::heavy_check_mark: / :house::ghost: | Cluster-internal certificate management
| ingress-operator  | N/A                   | :ocean::mortar_board: / :house::ghost: | HTTPS ingress to the cluster
| image-registry    | get, create, connect  | :ocean::heavy_check_mark: / :house::ghost: | Private Docker registry
| bastion           | N/A                   | :ocean::ghost: / :house::ghost: | VPN access for human operators
| postgresql        | N/A                   | :ocean::ghost: / :house::ghost: | Shared Postgresql database
| object-store      | N/A                   | :ocean::ghost: / :house::ghost: | Shared S3-compatible object store
| gitea             | N/A                   | :ocean::ghost: / :house::ghost: | Git repository hosting
| drone             | N/A                   | :ocean::ghost: / :house::ghost: | CI/CD task running

A single laboratory can include components in multiple clouds. By default the `default_cloud` in the `config.ini` is addressed, but this behavior can be overridden with the `-C` command-line flag.

# Getting Started

Requirements:

1. Python 3.8+ (tested with v3.8.2)
2. Poetry (tested with v1.0.5)
3. Binaries:
    - `kubectl` (tested with v1.18.0)
    - `kubecfg` (tested with v0.16.0)
    - `buildctl` (tested with v0.7.1)
    - `openssl` (tested with v1.1.1f)

Laboratory installation:

``` bash
# Clone the repository (installation via pip not currently recommended)
git clone https://github.com/luketurner/laboratory.git
cd laboratory

# install dependencies
poetry install

# Edit the config.ini and ensure all values are correct
vim config.ini

# Copy the example secret config into secret-config.ini
cp example-secret-config.ini secret-config.ini

# Edit the secret-config.ini and input the secrets you care about
vim secret-config.ioi

# test lab CLI (should display helptext)
poetry shell
lab --help
```

Deploying a cloud from scratch:

```bash
lab create network
lab create cluster
lab create node # optional, cluster starts with 1 node
lab create storage-operator
lab create cert-operator
lab create image-registry

# optional -- connect local `kubectl` and/or `docker` to the cloud
lab connect cluster > "${KUBECONFIG=~/.kube/config}"
lab connect image-registry > "~/.docker/config"
```