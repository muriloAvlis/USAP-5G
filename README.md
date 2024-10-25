# UE Smart Allocation Platform on Open 5G Networks (USAP)

The UE Smart Allocation Platform on Open 5G Networks (USAP) is a project to manage and optimize the allocation of UEs and UE QoS, using slices on Open 5G Networks with support for the ORAN Alliance O-RAN standard.

## Modules

- 5GC Slice Manager (muriloavlis/usap-sm) - Ok
- KPM Monitor (muriloavlis/usap-xapp) - Ok
- UE's slice classifier (muriloavlis/usap-ai) - In development

## Getting Started

### Requirements

- Kubernetes Cluster (tutorial in [K8s Installation Using Kubeadm](https://github.com/muriloAvlis/k8s-utils/blob/main/docs/cluster_deploy/kubeadm/install.md));
- OAI-5G Core (tutorial in [OAI-CN deploy](/docs/oai-cn/oai_cn_deploy.md));
- FlexRIC (tutorial in [FlexRIC deploy](https://github.com/muriloAvlis/flexric));
- OAI-5G RAN (tutorial in [OAI-RAN deploy](/docs/oai-ran/gnb_deploy.md));

### Network Slicing Configuration

#### 5GC Slice Types

|                    | **SST** | **SD** | **DNN** | **Subnet**  | **MCC** | **MNC** |
|--------------------|---------|--------|---------|-------------|---------|---------|
| **embb_slice**     | 1       | FFFFFF | embb  | 10.45.0.0/24 |   724   |   70    |
| **urllc_slice**    | 2       | FFFFFF | urllc  | 10.45.1.0/24 |   724   |   70    |
| **miot_slice**     | 3       | FFFFFF | miot  | 10.45.2.0/24 |   724   |   70    |
| **default_slice**  | 128     | FFFFFF | default  | 10.45.3.0/24 |   724   |   70    |

### Proposal topology

![proposal-topology-v1](./assets/images/proposal_topology.png)

### xApp Fluxogram

TODO

### How It Works

TODO