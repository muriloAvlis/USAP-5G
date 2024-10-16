# usap-xapp

## Requirements

- FlexRIC Service Models;
- gRPC;
- Protobuf;
- spdlog.

## Install Prerequisites

### On the Arch linux

```shell
sudo pacman -Syu grpc protobuf spdlog
```

### On the Ubuntu

```shell
## spdlog
sudo apt install -y libspdlog-dev

## gRPC and Protocol buffers
git clone --recurse-submodules -b v1.67.0 --depth 1 --shallow-submodules https://github.com/grpc/grpc && \
    cd grpc && \
    mkdir -p cmake/build && \
    cd cmake/build && \
    cmake -DgRPC_INSTALL=ON \
    -DgRPC_BUILD_TESTS=OFF ../.. && \
    make -j $(nproc) && \
    make install
```

## Building from source code

```shell
mkdir -p build && cd build
cmake -GNinja -DCMAKE_BUILD_TYPE=Release  ..
ninja xapp_usap
```