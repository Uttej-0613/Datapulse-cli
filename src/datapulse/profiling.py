import pandas as pd

def profile_csv(filepath: str) -> dict:
    frame = pd.read_csv(filepath)
    columns = []
    for name in frame.columns:
        series = frame[name]
        columns.append({"name": str(name), "dtype": str(series.dtype), "missing": int(series.isna().sum()), "missing_percent": round(float(series.isna().mean() * 100), 2), "unique": int(series.nunique(dropna=True)), "sample": [str(v) for v in series.dropna().head(3).tolist()]})
    return {"rows": int(len(frame)), "columns": int(len(frame.columns)), "duplicate_rows": int(frame.duplicated().sum()), "column_profiles": columns, "numeric_summary": frame.select_dtypes(include="number").describe().round(3).to_dict()}
