## Deployment USAP Application

To deploy USAP Application with Helm, run the following command:

```sh
cd ~/git/usap-5g/deployments/helm-chart/usap/
helm upgrade --install usap . -n ricxapp -f values.yaml --create-namespace
```