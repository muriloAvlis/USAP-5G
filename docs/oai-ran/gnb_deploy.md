# OAI gNodeB Deployment

## Requirements

- Kubernetes
- Helm v3

## Getting Started

### Clone oai-cn5g-fed repository

```sh
cd ~
git clone https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed.git
git checkout develop
```

### Install OAI-RAN gNodeB via Helm Chart

Copy the custom files in the configs folder to the chart directory and install them.

```sh 
cd ~/oai-cn5g-fed/charts/oai-5g-ran/oai-gnb
cp ~/USAP/configs/oai-ran/oai_gnb_values.yaml .
cp ~/USAP/configs/oai-ran/oai_gnb_configmap.yaml ./templates/configmap.yaml
helm dependency update
helm upgrade --install -n oairan --create-namespace oai-gnb . -f oai_gnb_values.yaml
```

### Clean up

```sh
helm uninstall -n oairan oai-gnb && kubectl delete ns oairan
```