USAP_XAPP_VER := latest

build_xapp:
	docker image build --tag muriloavlis/usap:${USAP_XAPP_VER} -f docker/Dockerfile.usap.xapp .