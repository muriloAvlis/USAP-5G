# Open5GS-CN Deployment

## Requirements

- Kubernetes (tested with 1.28)
- Helm v3

## Getting Started

### Clone the repository

```sh
cd ~
git clone https://github.com/muriloAvlis/USAP.git
```

### Install the core network with Helm

```sh
helm upgrade --install open5gs -n open5gs --create-namespace oci://registry-1.docker.io/gradiant/open5gs --version 2.2.2 -f ~/USAP/configs/open5gs-cn/open5gs_with_slices.yaml
```

> **_NOTE_**: [open5gs_with_slices.yaml](../../configs/open5gs-cn/open5gs_with_slices.yaml) example file.

> **_NOTE_**: nodeSelector is `kubernetes.io/hostname: open5gslocal`, change it if necessary.

The Open5GS GUI will be available at http://[open5gs-node-IP]:30999
- user: admin
- password: 1423