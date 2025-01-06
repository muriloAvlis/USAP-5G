include ./MakefileVars.mk

.PHONY: help

##@ Utility
help: ## Show this help.
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

build_usap: ## Build xApp docker image
	@echo "Building usap-xapp docker image"
	@docker image build -t muriloavlis/usap-xapp:${USAP_XAPP_VERSION} -f docker/Dockerfile.usap_xapp .

run_usap: ## Run xApp docker container
	@docker container run --rm -it --name usap-xapp muriloavlis/usap-xapp:${USAP_XAPP_VERSION}

push_usap: build_xapp ## Push xApp docker image to DockerHub
	@docker image push muriloavlis/usap-xapp:${USAP_XAPP_VERSION}

build_srs_cu_du: ## Build SRSRAN ZMQ docker image
	@echo "Building SRSRAN CU/DU docker image"
	@docker image build -t muriloavlis/srsran-5g:${SRSRAN_DOCKER_VERSION} --build-arg SRSRAN_VERSION=${SRSRAN_VERSION} -f docker/Dockerfile.srsran5g-zmq .

push_srs_cu_du: build_srs_cu_du ## Push SRSRAN ZMQ docker image to DockerHub
	@docker image push muriloavlis/srsran-5g:${SRSRAN_DOCKER_VERSION}

build_srsue: ## Build SRSUE ZMQ docker image
	@echo "Building SRSUE docker image"
	@docker image build -t muriloavlis/srsue:latest --build-arg SRSUE_VERSION=${SRSUE_VERSION} -f docker/Dockerfile.srsue .

push_srsue: build_srsue ## Push SRSRAN ZMQ docker image to DockerHub
	@docker image push muriloavlis/srsue:latest