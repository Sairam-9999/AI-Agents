"""Time-series preprocessing - gets your data ready for the LLM to munch on."""

import pandas as pd


def validate_timeseries(df, time_col="timestamp", value_cols=None):
    """Makes sure the data isn't broken - fixes timestamps, sorts them, fills gaps."""
    if value_cols is None:
        value_cols = [c for c in df.columns if c != time_col]

    if time_col not in df.columns:
        raise ValueError(f"Missing time column: {time_col}")

    df = df.copy()

    # Turn those strings into proper datetime objects
    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")

    if df[time_col].isnull().any():
        raise ValueError("Some timestamps could not be parsed")

    # Make sure everything's in chronological order
    if not df[time_col].is_monotonic_increasing:
        df = df.sort_values(time_col)

    # Patch up any holes in the data
    df[value_cols] = df[value_cols].ffill().bfill()

    return df


def timeseries_to_llm_chunks(
    df,
    time_col="timestamp",
    value_cols=None,
    chunk_size=20,
    overlap=5
):
    """Chops up time-series into bite-sized text chunks the LLM can handle."""

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