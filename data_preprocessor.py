"""
Time-series preprocessing utilities for LLM ingestion.
"""

import pandas as pd


def validate_timeseries(df, time_col="timestamp", value_cols=None):
    """
    Ensures time-series data is valid:
    - timestamp exists
    - sorted
    - no invalid timestamps
    - missing values filled
    """
    if value_cols is None:
        value_cols = [c for c in df.columns if c != time_col]

    if time_col not in df.columns:
        raise ValueError(f"Missing time column: {time_col}")

    df = df.copy()

    # Convert to datetime
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    if df[time_col].isnull().any():
        raise ValueError("Some timestamps could not be parsed")

    # Sort if not ordered
    if not df[time_col].is_monotonic_increasing:
        df = df.sort_values(time_col)

    # Fill missing values
    df[value_cols] = df[value_cols].ffill().bfill()

    return df


def timeseries_to_llm_chunks(
    df,
    time_col="timestamp",
    value_cols=None,
    chunk_size=20,
    overlap=5
):
    """
    Converts time-series into text chunks for LLM ingestion.
    """

    df = validate_timeseries(df, time_col=time_col, value_cols=value_cols)

    if value_cols is None:
        value_cols = [c for c in df.columns if c != time_col]

    rows = df[[time_col] + value_cols].to_dict("records")

    texts = []
    i = 0
    n = len(rows)

    while i < n:
        block = rows[i:i + chunk_size]

        lines = [
            f"{r[time_col].isoformat()} - " +
            ", ".join([f"{col}={r[col]}" for col in value_cols])
            for r in block
        ]

        texts.append("\n".join(lines))

        i += (chunk_size - overlap)

    return texts