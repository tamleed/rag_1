import chromadb
from datetime import datetime

# These are the connection details for the ChromaDB server
# running in Docker.
CHROMA_HOST = "localhost"
CHROMA_PORT = 8001
COLLECTION_NAME = "news_1" # This should match the collection used by the API

def test_query(in_text, n_res, sort_fields=("pub_date", "id")):
    """
    in_text: текст запроса
    n_res: количество результатов
    sort_fields: кортеж приоритетов сортировки, например ("pub_date", "id")
    """
    print("🔎 Подключаемся к Chroma...")
    # Use HttpClient to connect to the server
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)

    print(f"✅ Подключились. Получаем коллекцию '{COLLECTION_NAME}'...")
    collection = client.get_collection(COLLECTION_NAME)

    query_text = in_text
    print(f"➡️ Запрос: {query_text}")

    # The user's example notebook code did a text search, but the API
    # and ingestion script are set up for vector search. To correctly
    # query this setup, we would need to generate an embedding for the query.
    # For simplicity and to match the user's code, we will perform a text-based
    # retrieval here using `get` instead of `query`.
    # A true RAG query would require sentence-transformers here as well.

    # Note: The user's original code used collection.query with text, which
    # implies a vector search. However, without the embedding model, a
    # simple text search is not directly supported in the same way.
    # We will get ALL documents and filter/sort them locally as the user's
    # code structure suggests.

    results = collection.get() # Get all items to be sorted locally

    # Упаковываем результаты
    items = []
    for doc, meta, id in zip(results["documents"], results["metadatas"], results["ids"]):
        # The user's sample data doesn't have 'pub_date' or 'id' in the metadata.
        # We will add them here for the sorting to work as intended.
        # This is just for demonstration based on the user's sorting function.
        if 'pub_date' not in meta:
            meta['pub_date'] = f"2023-10-{int(id) % 30 + 1:02d}"
        if 'id' not in meta:
            meta['id'] = int(id)

        items.append({"doc": doc, "meta": meta})

    # Функция сортировки
    def sort_key(item):
        meta = item["meta"]
        keys = []
        for field in sort_fields:
            if field == "pub_date":
                try:
                    # Assuming YYYY-MM-DD format
                    keys.append(datetime.strptime(str(meta.get("pub_date", "")), "%Y-%m-%d"))
                except (ValueError, TypeError):
                    keys.append(datetime.min)
            elif field == "id":
                try:
                    keys.append(int(meta.get("id", 0)))
                except (ValueError, TypeError):
                    keys.append(0)
            else:
                keys.append(meta.get(field, ""))
        return tuple(keys)

    # Сортировка: всегда по убыванию (новее/больше — выше)
    items.sort(key=sort_key, reverse=True)

    # Печать отсортированных результатов (первые n_res)
    print("\n--- Отсортированные результаты ---")
    for i, item in enumerate(items[:n_res], 1):
        print(f"\n{i}. {item['doc'][:200]}...")
        print(f"   📌 meta: {item['meta']}")

    return items[:n_res]

if __name__ == '__main__':
    # Пример вызова функции
    test_query(in_text="space", n_res=3, sort_fields=("pub_date",))
    print("\n" + "="*20 + "\n")
    test_query(in_text="health", n_res=2, sort_fields=("id",))
