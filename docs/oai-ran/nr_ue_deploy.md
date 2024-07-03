# OAI NR-UE Deployment

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

### Install OAI-RAN NR-UE via Helm Chart

Copy the custom files in the configs folder to the chart directory and install them.

```sh 
cd ~/oai-cn5g-fed/charts/oai-5g-ran/oai-nr-ue
cp ~/QMPO5GNet/configs/oai-ran/oai_nr_ue_values.yaml .
cp ~/QMPO5GNet/configs/oai-ran/oai_nr_ue_configmap.yaml ./templates/configmap.yaml
helm dependency update
helm upgrade --install -n oairan --create-namespace oai-ue . -f oai_nr_ue_values.yaml
```

### Clean up

```sh
helm uninstall -n oairan oai-ue
```