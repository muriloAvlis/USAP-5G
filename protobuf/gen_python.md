# Build Python protobuf files

```sh
cd py_wrapper/app/server/proto
python -m grpc_tools.protoc -I . --python_out=../usap-classifier/app/pb/ --pyi_out=../usap-classifier/app/pb/ --grpc_python_out=../usap-classifier/app/pb/ xapp.proto
```