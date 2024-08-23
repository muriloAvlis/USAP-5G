ORAN_ASN1_CODER_VER := latest
USAP_XAPP_VER := latest

build_oranasn1coder:
	docker image build --tag muriloavlis/usap-oranasn1coder:${ORAN_ASN1_CODER_VER} -f docker/Dockerfile.usap.oranasn1coder .

build_usap_xapp:
	docker image build --tag muriloavlis/usap:${USAP_XAPP_VER} -f docker/Dockerfile.usap.xapp .