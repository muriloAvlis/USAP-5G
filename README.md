# QoS Management Platform on Open 5G Networks (QMPO5GNet)

The QoS Management Platform in 5G Networks (QMPO5GNet) is a project to manage and optimize QoS on Open 5G Networks
with support for the ORAN Alliance O-RAN standard.

## Table of Content

### 5GC

1. [OAI-CN Deployment](docs/oai-cn/oai_cn_deploy.md)
2. [Open5GS-CN Deployment](docs/open5gs-cn/open5gs_deploy.md)

### RAN

1. [OAI-RAN gNB Deployment](docs/oai-ran/gnb_deploy.md)
2. [OAI-RAN NR-UE Deployment](docs/oai-ran/nr_ue_deploy.md)

### RIC

1. [OSC Near-RT RIC Deployment](docs/osc-ric/osc_nrt_ric_deploy.md)

## Getting Started

### Requirements

- Kubernetes Cluster (tutorial on [K8s Installation Using the RKE2](https://github.com/muriloAvlis/k8s-utils/blob/main/docs/cluster_deploy/rke2/README.md))
- 5G Core (OAI-CN was used)
- 5G RAN (OAI-RAN was used)

### Slices Configuration

|                 | **sst** | **sd** | **dnn** | **Subnet** |
|-----------------|---------|--------|---------|-------------|
| **embb_slice**  | 1       | 000001 | nongbr  | 12.1.1.0/24 | 
| **urllc_slice** | 2       | 000001 | gbr     | 13.1.1.0/24 |
| **miot_slice**  | 3       | 000001 | iot     | 14.1.1.0/24 |
|                 |         |        |         |             |