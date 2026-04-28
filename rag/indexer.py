import os
import json

try:
    from rag.table_converter import table_to_text
except Exception:
    def table_to_text(path, max_rows=100):
        raise RuntimeError("table_to_text not available")


INDEX_DIR = "data/rag_index"
os.makedirs(INDEX_DIR, exist_ok=True)


def index_doc(symbol, text, meta=None):
    path = os.path.join(INDEX_DIR, f"{symbol}.json")

    record = {
        "symbol": symbol,
        "text": text,
        "meta": meta or {}
    }

    with open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(record))

    return path


def index_table_file(symbol, table_path):
    text = table_to_text(table_path)
    return index_doc(symbol, text, {"source": table_path})


def search(symbol):
    path = os.path.join(INDEX_DIR, f"{symbol}.json")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
