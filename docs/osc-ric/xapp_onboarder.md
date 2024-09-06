# xApp Onboarder

"xApp onboarder onboards xApp to the near-rt RIC platform. The operators provides the xApp descriptors and their schemas, the xApp onboarder generates the xApp helm charts dynamically." [OSC, 2024]

## Getting Starting

### Installation

```sh
#Git clone appmgr
git clone "https://gerrit.o-ran-sc.org/r/ric-plt/appmgr"

#Change dir to xapp_onboarder
cd appmgr/xapp_orchestrater/dev/xapp_onboarder

## Create a virtual environment
python3 -m venv .venv
. .venv/bin/activate

#Install xapp_onboarder using following command
pip install ./
```

### Onboarding xApp

Export enviroments and configurations files (check ricplt ingresses on K8s).

```sh
export CHART_REPO_URL=http://<ingress-ricplt-xapp-onboarder-chartmuseum.ricplt>/helmrepo
export FLASK_SERVER_NAME=http://<ingress-ricplt-xapp-onboarder-server.ricplt>/onboard
export CONFIG_FILE_PATH=~/git/usap-5g/deployments/helm/configs/config.json
export SCHEMA_FILE_PATH=~/git/usap-5g/deployments/helm/configs/schema.json
```

Onboarding the xApp with dms_cli.

```sh
dms_cli onboard --config_file_path=${CONFIG_FILE_PATH} --shcema_file_path=${SCHEMA_FILE_PATH}
```

### Get xApp Charts

List all charts

```sh
dms_cli get_charts_list
```

Or list specific xApp chart

```sh
curl -X GET http://<ingress-ricplt-xapp-onboarder-chartmuseum.ricplt>/helmrepo/api/charts/usapXapp/<VERSION> | jq .
# or
dms_cli get_charts_list --xapp_chart_name usapXapp
```

### Delete xApp Chart 

```sh
curl -X DELETE http://<ingress-ricplt-xapp-onboarder-chartmuseum.ricplt>/helmrepo/api/charts/<XAPP_CHART_NAME>/<VERSION>
```

### Download the xApp Helm Charts

```sh
export XAPP_CHART_NAME=usap
export XAPP_CHART_VERSION=0.0.1
export OUTPUT_PATH=~/git/usap-5g/deployments/helm-chart
dms_cli download_helm_chart --xapp_chart_name=${XAPP_CHART_NAME} --version=${XAPP_CHART_VERSION} --output_path=${OUTPUT_PATH}
```

### Install the xApp

```sh
export XAPP_NAMESPACE=ricxapp
dms_cli install --xapp_chart_name=${XAPP_CHART_NAME} --version=${XAPP_CHART_VERSION} --namespace=${XAPP_NAMESPACE}
```

### Uninstall the xApp

```sh
dms_cli uninstall --xapp_chart_name=${XAPP_CHART_NAME} --namespace=${XAPP_NAMESPACE}
```