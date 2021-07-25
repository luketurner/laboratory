# Laboratory

This repository has scripts for managing my DevOps laboratory.

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
| network           | get, create           | :ocean::heavy_check_mark: / :house::x: | Singleton network (VPC)
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

## DNS Notes

One thing not yet automated is registering a domain name and configuring A records for subdomains as needed by ingress.

This is a requirement for full cluster functionality, because some applications must be run with a consistent DNS name to function properly (e.g. for OAuth redirection.)

Assuming your domain is `foobar.com`, follow these steps:

1. After running `lab create ingress-operator`, determine the public IP address of your ingress node or load balancer, and put it in the A record for the following subdomains:
    - `gitea.foobar.com`
    - `drone.foobar.com`
2. Set the `root_dns_name` in `secret-config.ini` to `foobar.com`.

# Pyinfra

```

```