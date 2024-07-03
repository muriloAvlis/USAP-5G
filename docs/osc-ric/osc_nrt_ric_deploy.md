# OSC Near-RT RIC Deployment

## Requirements

- Kubernetes
- Helm v3

## Getting Starting

### Clone ric-dep repository

```sh
git clone "https://gerrit.o-ran-sc.org/r/ric-plt/ric-dep"
```

### Creating Platform and Xapp Namespaces

```sh
kubectl create ns ricplt
kubectl create ns ricxapp
```

### Running Chart Museum on Docker

```sh
docker run --rm -it \
  -u 0 \
  -p 6873:8080 \
  -e DEBUG=1 \
  -e STORAGE=local \
  -e STORAGE_LOCAL_ROOTDIR=/charts \
  -v $HOME/helm/chartsmuseum/:/charts \
  ghcr.io/helm/chartmuseum:v0.16.2
```

### Install Chartmuseum Plugin on the Helm

In another terminal, run the following command:

```sh
helm plugin install https://github.com/chartmuseum/helm-push
helm plugin list
```

### Add Local Repo on ChartMuseum Repo

```sh
helm repo add local http://localhost:6873/
helm repo list
```

### Install Dependencies on the Helm

```sh
helm repo add influxdata https://helm.influxdata.com
helm repo list
```

### Prepare Near-RT RIC Helm Charts

```sh
cd ~/ric-dep/new-installer/helm/charts
git checkout j-release
make nearrtric
```

Check if chart was installed (repeat `make nearrtric` if not)

```sh
helm search repo local/nearrtric
```

### Deploy Near-RT RIC

```sh
helm upgrade --install nearrtric -n ricplt local/nearrtric -f ~/QMPO5GNet/configs/osc-ric/osc_ric_values.yaml --create-namespace
```

## Clean up

```sh
helm uninstall -n ricplt nearrtric && kubectl delete ns ricplt
```