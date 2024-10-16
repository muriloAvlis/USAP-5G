# Build Python protobuf files

```sh
python -m grpc_tools.protoc -I . --python_out=../../usap-classifier/app/pb/ --pyi_out=../../usap-classifier/app/pb/ --grpc_python_out=../../usap-classifier/app/pb/ xapp.proto
```