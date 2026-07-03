import csv
from pathlib import Path
from .validators import validate_row

def load_and_clean_csv(filepath: str) -> list[dict]:
    """
    Reads a CSV, validates each row, and returns only clean rows.
    Also prints a validation summary to console.
    """
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    valid_rows = []
    invalid_rows = []
    
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            is_valid, errors = validate_row(row)
            if is_valid:
                # Convert to proper numeric types for ML
                valid_rows.append({
                    'age': int(row['age']),
                    'salary': float(row['salary'])
                })
            else:
                invalid_rows.append({'row': row, 'errors': errors})
    
    # Print summary (side-effect, but keeps our core logic pure)
    print(f"✅ Valid rows: {len(valid_rows)}")
    print(f"❌ Invalid rows: {len(invalid_rows)}")
    if invalid_rows:
        print("  (First error sample:)", invalid_rows[0]['errors'])
    
    return valid_rows
