# OAI CU-DU Deployment (F1 Split)

"The F1 interface is the functional split of 3GPP between the CU (centralized unit: PDCP, RRC, SDAP) and the DU (distributed unit: RLC, MAC, PHY). It is standardized in TS 38.470 - 38.473 for 5G NR. No equivalent for 4G exists." [OAI, 2024]

"We assume that each DU handles only one cell. Multiple DUs connected to one CU are supported. Mobility over F1 is not yet supported." [OAI, 2024]


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

### TODO