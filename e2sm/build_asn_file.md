# Compile asn file with asn1c

```sh
 asn1c -fcompound-names -fincludes-quoted -fno-include-deps -findirect-choice ../asn1/e2sm-v5.00.asn ../asn1/e2sm-kpm-v4.00.asn
```

## Rewrite converter-example.c

To avoid a Go error `A reference to undefined reference 'ASN_DEF_1'`:

```shell
echo "int main(){}" > converter-example.c
```