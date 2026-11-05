import tempfile
from pathlib import Path
import streamlit as st
import plotly.express as px
import pandas as pd
from datapulse.database import ingest_csv, list_tables
from datapulse.profiling import profile_csv
from datapulse.sql_guard import execute_readonly
from datapulse.nl2sql import ask

st.set_page_config(page_title="DataPulse | Analytics", page_icon="◈", layout="wide")
st.markdown("<style>.stApp{background:linear-gradient(145deg,#0b1220,#111c2d);color:#eaf1ff}[data-testid='stMetric']{background:#142238;border:1px solid #263a58;padding:16px;border-radius:14px}section[data-testid='stSidebar']{background:#0c1728}h1,h2,h3{letter-spacing:-.035em}</style>", unsafe_allow_html=True)
st.title("◈ DataPulse")
st.caption("DATA WORKSPACE / PROFILE · INGEST · QUERY · UNDERSTAND")
tab_data, tab_sql, tab_ai = st.tabs(["Dataset studio", "SQL explorer", "Ask your data"])
with tab_data:
    upload = st.file_uploader("Upload a CSV dataset", type=["csv"])
    table = st.text_input("Table name (optional)")
    if upload and st.button("Profile and ingest"):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as temp:
            temp.write(upload.getvalue())
            path = Path(temp.name)
        try:
            profile = profile_csv(str(path))
            result = ingest_csv(path, table or None)
            st.success(f"Loaded {result['rows']:,} rows into {result['table']}")
            a,b,c = st.columns(3)
            a.metric("Rows", f"{profile['rows']:,}")
            b.metric("Columns", profile["columns"])
            c.metric("Duplicate rows", profile["duplicate_rows"])
            st.dataframe(pd.DataFrame(profile["column_profiles"]), use_container_width=True)
            st.json(profile["numeric_summary"])
        finally:
            path.unlink(missing_ok=True)
    st.subheader("Available tables")
    st.json(list_tables())
with tab_sql:
    sql = st.text_area("Read-only SQL", "SELECT name FROM sqlite_master WHERE type='table';", height=130)
    if st.button("Run query"):
        try:
            result = execute_readonly(sql)
            st.code(result["sql"], language="sql")
            frame = pd.DataFrame(result["rows"])
            st.dataframe(frame, use_container_width=True)
            st.caption(f"{result['row_count']} rows returned")
            if not frame.empty:
                st.download_button("Download CSV", frame.to_csv(index=False), "datapulse_results.csv", "text/csv")
        except Exception as exc: st.error(str(exc))
with tab_ai:
    st.write("Ask a question in plain English. Generated SQL passes through the read-only safety gate.")
    question = st.text_input("Question", placeholder="Which departments have the highest average salary?")
    if st.button("Generate SQL and analyze"):
        try:
            result = ask(question)
            st.code(result["sql"], language="sql")
            frame = pd.DataFrame(result["rows"])
            st.dataframe(frame, use_container_width=True)
            numeric = frame.select_dtypes(include="number").columns.tolist()
            if len(frame.columns) >= 2 and numeric:
                st.plotly_chart(px.bar(frame, x=frame.columns[0], y=numeric[0], template="plotly_dark"), use_container_width=True)
        except Exception as exc: st.error(str(exc))
st.caption("Local-first analytics. AI SQL requires OPENAI_API_KEY. Review generated SQL and business assumptions.")
