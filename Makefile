.PHONY: build

QMAI_REPO    := muriloavlis/qmai
QMAI_VERSION := dev

build: # @HELP build the Go binary of the qmai xAPP
	@go build -v -o build/_output/qmai ./cmd/qmai
	
docker-build: # @HELP build the qmai docker image
	@docker image build -t ${QMAI_REPO}:${QMAI_VERSION} -f build/Dockerfile .

docker-push: docker-build # @HELP push image to Docker Hub
	@docker image push ${QMAI_REPO}:${QMAI_VERSION}

clean: # @HELP remove all the build artifacts
	rm -rf ./build/_output