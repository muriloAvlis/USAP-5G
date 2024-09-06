# UE Smart Allocation Platform on Open 5G Networks (USAP)

The UE Smart Allocation Platform on Open 5G Networks (USAP) is a project to manage and optimize the allocation of UEs and UE QoS, using slices on Open 5G Networks with support for the ORAN Alliance O-RAN standard.

<!-- ## Tutorials

### 5GC

1. [OAI-CN Deployment](docs/oai-cn/oai_cn_deploy.md)
2. [Open5GS-CN Deployment](docs/open5gs-cn/open5gs_deploy.md)

### RAN

1. [OAI-RAN gNB Deployment](docs/oai-ran/gnb_deploy.md)
2. [OAI-RAN NR-UE Deployment](docs/oai-ran/nr_ue_deploy.md)
3. [SRS-RAN 5G gNB + UE Deployment](./docs/srsran/srsran5g_zmq_deploy.md)

### RIC

1. [OSC Near-RT RIC Deployment](docs/osc-ric/osc_nrt_ric_deploy.md) -->

## Standardizations

Definitions used by the application to interact with the RIC

### E2SM standard

- [E2SM-KPM-v4.00](oranASN1Coder/asn1/e2sm/e2sm-kpm-v4.00.asn)
- [E2SM-RC-v5.00](oranASN1Coder/asn1/e2sm/e2sm-rc-v5.00.asn)
- [E2SM-v5.00](oranASN1Coder/asn1/e2sm/e2sm-v5.00.asn)

<!-- ### 3GPP NG Application Protocol (NGAP) Release 17

- [NGAP-CommonDataTypes](ngap/asn1/rel-18_2/NGAP-CommonDataTypes.asn)
- [NGAP-Constants](ngap/asn1/rel-18_2/NGAP-Constants.asn)
- [NGAP-Containers](ngap/asn1/rel-18_2/NGAP-Containers.asn)
- [NGAP-IEs](ngap/asn1/rel-18_2/NGAP-IEs.asn)
- [NGAP-PDU-Contents](ngap/asn1/rel-18_2/NGAP-PDU-Contents.asn)
- [NGAP-PDU-Descriptions](ngap/asn1/rel-18_2/NGAP-PDU-Descriptions.asn) -->

## Getting Started

### Requirements

- Kubernetes Cluster (tutorial on [K8s Installation Using Kubeadm](https://github.com/muriloAvlis/k8s-utils/blob/main/docs/cluster_deploy/kubeadm/install.md))
- 5G Core (Open5GS was used)
- 5G RAN (SRSRAN was used)

### Build Docker Image

```sh
docker image build -t muriloavlis/usap:latest -f docker/Dockerfile.usap .
```

### Network Slicing Configuration

#### NFs

|                    | **SST** | **SD** |
|--------------------|---------|--------|
| **SMF/UPF-eMBB**     | 1       | 0x1  | 
| **SMF/UPF-URLLC**    | 2       | 0x1  |
| **SMF/UPF-mIoT**     | 3       | 0x1  |
| **SMF/UPF-default**  | 4       | 0x1  |

#### Service Types 

|                    | **SST** | **SD** | **DNN** | **Subnet**  | **MCC** | **MNC** |
|--------------------|---------|--------|---------|-------------|---------|---------|
| **embb_slice**     | 1       | 000001 | internet  | 10.45.0.0/24 |   724   |   70    |
| **urllc_slice**    | 2       | 000001 | internet  | 10.45.1.0/24 |   724   |   70    |
| **miot_slice**     | 3       | 000001 | internet  | 10.45.2.0/24 |   724   |   70    |
| **default_slice**  | 4       | 000001 | internet  | 10.45.3.0/24 |   724   |   70    |

### Proposal topology

![proposal-topology-v1](./assets/images/proposal_topology.png)

### xApp Fluxogram

TODO

### How It Works

TODO