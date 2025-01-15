# Build Python protobuf files

- E2SM

```sh
python3 -m grpc_tools.protoc -I . --python_out=../usap-e2sm/usap_e2sm/pb/ --pyi_out=../usap-e2sm/usap_e2sm/pb/ --grpc_python_out=../usap-e2sm/usap_e2sm/pb/ e2sm.proto
```

- SMC

```sh
python3 -m grpc_tools.protoc -I . --python_out=../usap-smc/usap_smc/pb/ --pyi_out=../usap-smc/usap_smc/pb/ --grpc_python_out=../usap-smc/usap_smc/pb/ xapp.proto 
```