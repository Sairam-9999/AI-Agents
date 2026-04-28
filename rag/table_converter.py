import pandas as pd
import os


def table_to_text(path: str, max_rows=100):
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    ext = os.path.splitext(path)[1].lower()

    if ext == ".csv":
        df = pd.read_csv(path)
    elif ext in (".xls", ".xlsx"):
        df = pd.read_excel(path)
    else:
        raise ValueError("Unsupported table format: " + ext)

    rows = df.head(max_rows).to_dict(orient="records")
    parts = []

    for i, r in enumerate(rows):
        parts.append(
            f"Row {i + 1}: " +
            ", ".join([f"{k}={v}" for k, v in r.items()])
        )

    return "\n".join(parts)
