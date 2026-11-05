import pandas as pd
from datapulse.validation import validate_frame

def test_missing_values_are_rejected():
    frame = pd.DataFrame({"name": ["Ada", None], "age": [36, 22]})
    valid, rejected = validate_frame(frame)
    assert len(valid) == 1
    assert len(rejected) == 1
    assert "name: missing value" in rejected.iloc[0]["errors"]
