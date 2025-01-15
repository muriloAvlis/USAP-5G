# Build Go protobuf files

- e2sm

```sh
protoc --go_out=../pkg/ --go-grpc_out=../pkg/ e2sm.proto
```

- xapp

```sh
protoc --go_out=../pkg/ --go-grpc_out=../pkg/ xapp.proto
```