# Build Go protobuf files

```sh
protoc --go_out=../usap-xapp/pkg/ --go-grpc_out=../usap-xapp/pkg/ xapp.proto
```