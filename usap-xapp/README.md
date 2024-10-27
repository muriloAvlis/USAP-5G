# usap-xapp

## Requirements

- Ubuntu (22.04 or 24.04);
- FlexRIC Service Models;
- gRPC;
- Protobuf;
- spdlog.

## Install Prerequisites

### Ubuntu packages

```shell
sudo apt install -y libsctp-dev cmake-curses-gui libpcre2-dev libspdlog-dev python3-dev
```

### gRPC and Protobuf

```shell
git clone --recurse-submodules -b v1.67.0 --depth 1 --shallow-submodules https://github.com/grpc/grpc && \
    cd grpc && \
    mkdir -p cmake/build && \
    cd cmake/build && \
    cmake -DgRPC_INSTALL=ON \
    -DgRPC_BUILD_TESTS=OFF ../.. && \
    make -j $(nproc) && \
    sudo make install
```

### FlexRIC SMs

TODO:

```shell

```

## Building from source code

```shell
mkdir -p build && cd build
cmake -GNinja -DCMAKE_BUILD_TYPE=Release  ..
ninja xapp_usap
```

## Running xapp

```shell
./xapp_usap -c ../config/xapp.conf
```