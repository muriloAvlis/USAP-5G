# Build Python protobuf files

```sh
cd py_wrapper/app/server/proto
python -m grpc_tools.protoc -I ../../../../protobuf --python_out=. --pyi_out=. --grpc_python_out=. ../../../../protobuf/e2sm.proto
```