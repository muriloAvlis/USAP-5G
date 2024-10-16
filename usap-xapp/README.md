# usap-xapp

## Requirements

- gRPC;
- Protobuf;
- spdlog.

## Install Prerequisites

### Arch linux

```shell
sudo pacman -Syu grpc protobuf spdlog
```

### Ubuntu

```shell
sudo apt install -y libspdlog-dev protobuf-compiler-grpc
```

## Building from source code

```shell
mkdir -p build
cmake -GNinja ..
ninja xapp_usap
```