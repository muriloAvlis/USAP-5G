# FlexRIC Deploy

## Requirements

- Kubernetes
- Helm

## Getting Starting

### Helm install

```sh
cd ~/git/flexric/helm-chart/flexric
helm upgrade --install flexric -n flexric . --create-namespace -f usapValues.yaml
```

### Clean up

```sh
helm uninstall -n flexric flexric && kubectl delete ns flexric
```