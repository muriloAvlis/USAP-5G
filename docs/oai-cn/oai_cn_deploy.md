# OAI 5G Core Network Deployment

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

### Install OAI-5G CN via Helm Chart

```sh 
cd ~/oai-cn5g-fed/charts/oai-5g-core/oai-5g-advance
helm dependency update
helm install -n oai5gcn --create-namespace oai5gcn . -f oai_cn_values.yaml
```