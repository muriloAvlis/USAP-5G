# OAI gNodeB Deployment

## Requirements

- Kubernetes
- Helm v3

## Getting Started

<!-- ### Clone oai-cn5g-fed repository

```sh
cd ~
git clone https://gitlab.eurecom.fr/oai/cn5g/oai-cn5g-fed.git
git checkout develop
``` -->

### Install OAI-RAN gNodeB via Helm Chart

Copy the custom files in the configs folder to the chart directory and install them.

```sh 
cd ~/git/usap-5g/charts/oai-5g-ran/oai-gnb
helm dependency update
helm upgrade --install -n oairan --create-namespace oai-gnb . -f oai_gnb_values.yaml
```

### Clean up

```sh
helm uninstall -n oairan oai-gnb && kubectl delete ns oairan
```