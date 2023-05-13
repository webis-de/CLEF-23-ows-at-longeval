IMAGE_VERSION=0.0.1

build-docker-images:
	docker build -t mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} -f src/Dockerfile.ir_datasets src

push-docker-images:
	docker push mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION}

