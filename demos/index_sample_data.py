from rag.indexer import index_doc, index_table_file

if __name__ == "__main__":
    # Grab the fake 10-K filing
    with open("data/docs/TEST_10K.txt", "r", encoding="utf-8") as f:
        txt = f.read()

    # Throw it into the search index
    index_doc("TEST", txt, {"source": "data/docs/TEST_10K.txt"})

    # Index that CSV table too
    index_table_file("TEST_TABLE", "data/sample_table.csv")

    print("Indexed TEST and TEST_TABLE")
