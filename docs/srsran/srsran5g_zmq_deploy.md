# SRSRAN-5G Deployment

## Requirements

- Kubernetes (tested with 1.29)
- Helm v3
- A Storage Class

## Getting Started

### Clone the repository

```sh
cd ~/git
git clone https://github.com/gercom-ufpa/srsran-5g
```

### Install the core network with Helm

```sh
cd ~/git/srsran-5g/charts/srsran-5g
helm dependency build
helm upgrade --install srsran-gnb -n srsran --create-namespace . -f ~/git/USAP/configs/srsran/values-gnb-zmq.yaml
```

> **_NOTE_**: nodeSelector is `kubernetes.io/hostname: 5gran`, change it if necessary.

### Clean up

```sh
helm uninstall -n srsran srsran-gnb && kubectl delete ns srsran
```