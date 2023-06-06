"""This python file registers new ir_datasets classes for 'longeval'.
   You can find the ir_datasets documentation here: https://github.com/allenai/ir_datasets/.
   This file is intended to work inside the Docker image.
"""
import ir_datasets
from ir_datasets.formats import TrecDocs, TrecQueries, TrecQrels, TsvQueries
from typing import NamedTuple, Dict
from ir_datasets.datasets.base import Dataset
from ir_datasets.util import LocalDownload
from ir_datasets.indices import PickleLz4FullStore
from pathlib import Path

class LongEvalDocs(TrecDocs):
    def __init__(self, dlc):
        self._dlc = LocalDownload(Path(dlc))
        super().__init__(self._dlc)

    def docs_store(self):
        return PickleLz4FullStore(
            path=f'{self._dlc.path(force=False)}.pklz4',
            init_iter_fn=self.docs_iter,
            data_cls=self.docs_cls(),
            lookup_field='doc_id',
            index_fields=['doc_id'],
        )

ir_datasets.registry.register('longeval/train', Dataset(
    LongEvalDocs('/root/.ir_datasets/longeval/publish/English/Documents/Trec/'),
    TsvQueries(LocalDownload(Path('/root/.ir_datasets/longeval/publish/English/Queries/train.tsv'))),
    TrecQrels(LocalDownload(Path('/root/.ir_datasets/longeval/publish/French/Qrels/train.txt')), {0: 'Not Relevant', 1: 'Relevant', 2: 'Highly Relevant'})
))

ir_datasets.registry.register('longeval/heldout', Dataset(
    LongEvalDocs('/root/.ir_datasets/longeval/publish/English/Documents/Trec/'),
    TsvQueries(LocalDownload(Path('/root/.ir_datasets/longeval/publish/English/Queries/heldout.tsv'))),
    TrecQrels(LocalDownload(Path('/root/.ir_datasets/longeval/longeval-relevance-judgements/heldout-test.txt')), {0: 'Not Relevant', 1: 'Relevant', 2: 'Highly Relevant'})
))

ir_datasets.registry.register('longeval/a-short-july', Dataset(
    LongEvalDocs('/root/.ir_datasets/longeval/test-collection/A-Short-July/English/Documents/Trec/'),
    TsvQueries(LocalDownload(Path('/root/.ir_datasets/longeval/test-collection/A-Short-July/English/Queries/test07.tsv'))),
    TrecQrels(LocalDownload(Path('/root/.ir_datasets/longeval/longeval-relevance-judgements/a-short-july.txt')), {0: 'Not Relevant', 1: 'Relevant', 2: 'Highly Relevant'})
))

ir_datasets.registry.register('longeval/b-long-september', Dataset(
    LongEvalDocs('/root/.ir_datasets/longeval/test-collection/B-Long-September/English/Documents/Trec/'),
    TsvQueries(LocalDownload(Path('/root/.ir_datasets/longeval/test-collection/B-Long-September/English/Queries/test09.tsv'))),
    TrecQrels(LocalDownload(Path('/root/.ir_datasets/longeval/longeval-relevance-judgements/b-long-september.txt')), {0: 'Not Relevant', 1: 'Relevant', 2: 'Highly Relevant'})
))
