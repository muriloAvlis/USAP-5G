# SRSRAN-5G Deployment

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
cd ~/USAP/charts/srsran-5g-zmq
helm dependency build
helm upgrade --install srsran5g -n srsran --create-namespace . -f ~/USAP/configs/srsran/srsran5g_zqm_values.yaml
```

> **_NOTE_**: nodeSelector is `kubernetes.io/hostname: oairan`, change it if necessary.

### Clean up

```sh
helm uninstall -n srsran srsran5g && kubectl delete ns srsran
```