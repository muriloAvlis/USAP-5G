# Open5GS Core Network

## Requirements

- Kubernetes
- Helm v3

## Getting Started

### Open5GS K8s Deployment

Clone the repository

```sh
cd ~
git clone https://github.com/muriloAvlis/usap-5g.git
cd charts/open5gs
```

Install the core network with Helm

```sh
helm upgrade --install open5gs -n open5gs --create-namespace chart/open5gs --version 2.2.6 -f ./configs/values-cloud5.yaml
```

> **_NOTE_**: nodeSelector is `kubernetes.io/hostname: open5gslocal`, change it if necessary.

The Open5GS GUI will be available at http://[open5gs-node-IP]:30999

- user: admin
- password: 1423


## Clean up

```sh
helm uninstall -n open5gs-usap open5gs && kubectl delete ns open5gs
```