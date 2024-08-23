# Build Go protobuf files

```sh
protoc --go_out=../pkg/ --go-grpc_out=../pkg/ e2sm.proto
```