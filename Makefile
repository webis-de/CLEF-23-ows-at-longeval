IMAGE_VERSION=0.0.1

build-docker-images:
	docker build -t mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} -f src/Dockerfile.ir_datasets src

push-docker-images:
	docker push mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION}

ir-datasets-index-train:
	docker run -rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_train.py

ir-datasets-index-test-short-july:
	docker run -rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_test_short_july.py

ir-datasets-index-test-long-september:
	docker run -rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_test_long_september.py

