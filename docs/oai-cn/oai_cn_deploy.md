# OAI 5G Core Network Deployment

## Requirements

- Kubernetes
- Helm v3

## Getting Started

### Clone oai-cn5g-fed repository

```sh
cd ~/git
git clone https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed.git
cd oai-cn5g-fed
git checkout develop
```

### Install OAI-5G CN via Helm Chart

Copy the custom files in the configs folder to the chart directory and install them.

```sh 
cd ~/git/oai-cn5g-fed/charts/oai-5g-core/oai-5g-advance
cp ~/git/USAP/configs/oai-cn/* .
helm dependency update
helm upgrade --install -n oai5gcn --create-namespace oai-5gcn . -f values.yaml
```

### Clean up

```sh
helm uninstall -n oai5gcn oai-5gcn && kubectl delete ns oai5gcn
```