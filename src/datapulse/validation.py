import pandas as pd

def validate_frame(frame):
    errors = []
    for index, row in frame.iterrows():
        row_errors = [f"{column}: missing value" for column, value in row.items() if pd.isna(value)]
        if row_errors:
            errors.append({"row_number": int(index) + 2, "errors": row_errors})
    bad = {item["row_number"] - 2 for item in errors}
    return frame.drop(index=list(bad)).copy(), pd.DataFrame(errors, columns=["row_number", "errors"])

def validate_csv(filepath):
    frame = pd.read_csv(filepath)
    valid, rejected = validate_frame(frame)
    return {"total_rows": len(frame), "valid_rows": len(valid), "rejected_rows": len(rejected), "valid": valid, "rejected": rejected}
