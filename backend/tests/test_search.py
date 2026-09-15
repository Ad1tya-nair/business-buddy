from app.services.indexer import rebuild_index


store = rebuild_index()

results = store.search(
    "What reliability problems were discussed?",
    top_k=3,
)

for result in results:
    print(result)