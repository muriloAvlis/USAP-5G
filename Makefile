.PHONY: build

QMAI_REPO    := muriloavlis/qmai
QMAI_VERSION := latest

build: # @HELP build the Go binary of the qmai xAPP
	@go build -v -o build/_output/qmai ./cmd/qmai
	
docker-build: # @HELP build the qmai docker image
	@docker image build -t ${QMAI_REPO}:${QMAI_VERSION} -f build/Dockerfile .

docker-push: docker-build # @HELP push image to Docker Hub
	@docker image push ${QMAI_REPO}:${QMAI_VERSION}

helm-install:
	@helm upgrade --install qmai -n riab ./deployments/helm-chart/qmai/

helm-uninstall:
	@helm uninstall -n riab qmai

dev-ops: docker-push helm-uninstall helm-install

k8s-logs:
	@kubectl logs -n riab $$(kubectl get pods -n riab --no-headers -o custom-columns=":metadata.name" | grep qmai) qmai -f

clean: # @HELP remove all the build artifacts
	rm -rf ./build/_output