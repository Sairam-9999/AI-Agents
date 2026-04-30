from rag.indexer import index_doc, index_table_file

if __name__ == "__main__":
    # Read mock document
    with open("data/docs/TEST_10K.txt", "r", encoding="utf-8") as f:
        txt = f.read()

    # Index document
    index_doc("TEST", txt, {"source": "data/docs/TEST_10K.txt"})

    # Index table
    index_table_file("TEST_TABLE", "data/sample_table.csv")

    print("Indexed TEST and TEST_TABLE")
