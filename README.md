# Laboratory

This repository has scripts for managing my DevOps laboratory.

When it comes to DevOps, I believe you don't _understand_ it unless you can _automate_ it. So, laboratory operations are entirely wrapped up in a repeatable, idempotent CLI called `lab`.

> **Warning:** Like my laboratory itself, this CLI is a _personal project_. A core purpose of the project is _learning_. I've provided it as reference and inspiration, not as a polished software product you should use.

# Quick Reference

The laboratory is broken into semi-independent "features". The `lab` CLI uses a `lab VERB NOUN...` format, where `NOUN` is one or more feature names.

The following table indicates which features are supported or planned.
For compactness, pairs of emoji are used to indicate status. The left emoji indicates the cloud, and the right emoji indicates the status for that cloud.

- Clouds: :ocean: Digital Ocean (managed) / :house: Pi Homelab
- Statuses: :x: Not planned or N/A / :ghost: Planned, not started / :mortar_board: Learning/Planning / :heavy_check_mark: Finished 

| Feature name | Verbs | Status | Notes
|-|-|-|-|
| network | get, create | :ocean::heavy_check_mark: :house::ghost: | Singleton network (VPC)
| cluster | get, create | Working | Singleton Kubernetes cluster
| node | create, delete | untested | Manage nodes in the cluster
| storage-operator | N/A | WIP | 
| ingress-operator | N/A | WIP | 
| cert-operator | N/A | WIP | 
| bastion | N/A | WIP | 
| image-registry | N/A | WIP | 
| postgresql | N/A | WIP | 
| object-store | N/A | WIP | 

A single laboratory can include components in multiple clouds. By default the `default_cloud` in the `config.ini` is addressed, but this behavior can be overridden with the `-C` command-line flag.

# Getting Started

Requirements:

1. Python 3.8+ (tested with v3.8.2)
2. Poetry (tested with v1.0.5)
3. Binaries:
    - `kubectl` (tested with v1.18.0)
    - `kubecfg` (tested with v0.16.0)
    - `buildctl` (tested with v0.7.1)

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
poetry run lab --help
```