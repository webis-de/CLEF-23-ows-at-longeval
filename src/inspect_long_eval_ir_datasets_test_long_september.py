import ir_datasets

data = ir_datasets.load('longeval/b-long-september')
docs_store = data.docs_store()
print(docs_store().get('doc062201000001'))

