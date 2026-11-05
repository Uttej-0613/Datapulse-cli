import sqlite3
import pytest
from datapulse.sql_guard import validate_select, execute_readonly, UnsafeQuery

def test_select_is_allowed_and_limited():
    assert "LIMIT" in validate_select("SELECT 1").upper()

@pytest.mark.parametrize("sql", ["DROP TABLE users", "DELETE FROM users", "SELECT 1; SELECT 2", "PRAGMA table_info(users)", "ATTACH DATABASE 'x' AS x"])
def test_unsafe_sql_is_rejected(sql):
    with pytest.raises(UnsafeQuery):
        validate_select(sql)

def test_readonly_query_executes(tmp_path):
    db = tmp_path / "test.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE people(name TEXT, age INTEGER)")
    con.execute("INSERT INTO people VALUES('Ada', 36)")
    con.commit()
    con.close()
    result = execute_readonly("SELECT name, age FROM people", db)
    assert result["rows"] == [{"name": "Ada", "age": 36}]
