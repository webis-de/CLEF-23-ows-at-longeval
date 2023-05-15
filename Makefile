IMAGE_VERSION=0.0.2

build-docker-images:
	docker build -t mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} -f src/Dockerfile.ir_datasets src

push-docker-images:
	docker push mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION}

jupyter:
	docker run --rm -ti -p 8888:8888 \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint jupyter mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		notebook --allow-root --ip 0.0.0.0

retrieval-jupyter:
	docker run --rm -ti -p 8889:8888 \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-v /mnt/ceph/tira:/mnt/ceph/tira:ro \
		-w /home/jovyan/work \
		--entrypoint jupyter \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		notebook --allow-root --ip 0.0.0.0

produce-query-expansion:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}/src:/workspace -w /workspace \
		--entrypoint sh \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION}

ir-datasets-index-train:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}/src:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_train.py

ir-datasets-index-test-short-july:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}/src:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_test_short_july.py

ir-datasets-index-test-long-september:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets \
		-v $${PWD}/src:/workspace -w /workspace \
		--entrypoint python3 \
		mam10eks/ows-long-eval-ir-datasets-integration:${IMAGE_VERSION} \
		inspect_long_eval_ir_datasets_test_long_september.py


irds-export-train:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v ${PWD}/src:/workspace \
		-v /mnt/ceph/tira/data/datasets/training-datasets/ir-benchmarks/longeval-train-20230513-training:/out \
		mam10eks/ows-long-eval-ir-datasets-integration:0.0.1 \
		--ir_datasets_id longeval/train \
		--output_dataset_path /out \
		--skip_qrels true \
		--include_original false


irds-export-heldout:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v ${PWD}/src:/workspace \
		-v /mnt/ceph/tira/data/datasets/training-datasets/ir-benchmarks/longeval-heldout-20230513-training:/out \
		mam10eks/ows-long-eval-ir-datasets-integration:0.0.1 \
		--ir_datasets_id longeval/heldout \
		--output_dataset_path /out \
		--skip_qrels true \
		--include_original false

irds-export-short-july:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v ${PWD}/src:/workspace \
		-v /mnt/ceph/tira/data/datasets/training-datasets/ir-benchmarks/longeval-short-july-20230513-training:/out \
		mam10eks/ows-long-eval-ir-datasets-integration:0.0.1 \
		--ir_datasets_id longeval/a-short-july \
		--output_dataset_path /out \
		--skip_qrels true \
		--include_original false

irds-export-long-september:
	docker run --rm -ti \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v ${PWD}/src:/workspace \
		-v /mnt/ceph/tira/data/datasets/training-datasets/ir-benchmarks/longeval-long-september-20230513-training:/out \
		mam10eks/ows-long-eval-ir-datasets-integration:0.0.1 \
		--ir_datasets_id longeval/b-long-september \
		--output_dataset_path /out \
		--skip_qrels true \
		--include_original false



bm25-plain-long:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./plain-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-long-september-20230513-training BM25

bm25-plain-short:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./plain-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-short-july-20230513-training BM25

bm25-plain-train:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./plain-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-train-20230513-training BM25

bm25-query-variant-long:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./query-variant-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-long-september-20230513-training BM25

bm25-query-variant-short:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./query-variant-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-short-july-20230513-training BM25

bm25-query-variant-train:
	docker run --rm -ti \
		-v /mnt/ceph/storage/data-tmp/current/kibi9872/pan-code/semeval23/.tira:/root/.tira \
		-v /mnt/ceph/tira/state/ir_datasets/:/root/.ir_datasets:ro \
		-v "$${PWD}/src":/home/jovyan/work \
		-w /home/jovyan/work \
		--entrypoint ./query-variant-rerank.py \
		webis/tira-ir-starter-pyterrier:0.0.2-base \
		longeval-train-20230513-training BM25
