# Build Python protobuf files

```sh
python -m grpc_tools.protoc -I ../../../../xapp/pb --python_out=. --pyi_out=. --grpc_python_out=. xapp.proto
```