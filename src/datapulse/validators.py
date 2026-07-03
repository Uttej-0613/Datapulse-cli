"""Reusable data validation rules (no file I/O, pure logic)"""

def validate_row(row: dict) -> tuple[bool, list[str]]:
    """
    Validate a single data row.
    Returns: (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Rule 1: Age must be a positive integer
    try:
        age = int(row.get('age', 0))
        if age <= 0:
            errors.append(f"Age must be > 0 (got {age})")
    except (ValueError, TypeError):
        errors.append(f"Age must be an integer (got '{row.get('age')}')")
    
    # Rule 2: Salary must be a non-negative number
    try:
        salary = float(row.get('salary', -1))
        if salary < 0:
            errors.append(f"Salary must be >= 0 (got {salary})")
    except (ValueError, TypeError):
        errors.append(f"Salary must be a number (got '{row.get('salary')}')")
    
    return len(errors) == 0, errors
