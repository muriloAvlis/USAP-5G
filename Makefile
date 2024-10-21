include .env

build_xapp:
	@docker image build --tag muriloavlis/usap-xapp:${XAPP_VER} -f docker/Dockerfile.usap.xapp .

build_sm:
	@docker image build --tag muriloavlis/usap-sm:${XAPP_VER} -f docker/Dockerfile.usap.sm .

docker_push_xapp:
	@docker image push muriloavlis/usap-xapp:${XAPP_VER}