# SD-RAN Installation

## Requirements

- K8s
- Helm

## Dependencies on K8s

### micro-onos/nrt-RIC

- Atomix Controller

```bash
helm install -n kube-system atomix-controller atomix/atomix-controller --version 0.6.9
helm install -n kube-system atomix-raft-storage atomix/atomix-raft-storage
```

- ONOS Operator

```bash
helm install -n kube-system onos-operator onosproject/onos-operator
```

- micro-onos umbrella

```bash
helm -n micro-onos install onos-umbrella onosproject/onos-umbrella --version 1.2.51
```

### SD-RAN

```bash
git clone https://github.com/onosproject/sdran-helm-charts.git \
cd sdran-helm-charts/sd-ran \
git checkout sd-ran-1.4.5 \
helm dependency build \
kubectl create ns sd-ran \
helm install sd-ran -n sd-ran .
```
