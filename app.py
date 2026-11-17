"""Streamlit interface for the Data Cleaning Agent."""

import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from data_cleaning_agent import LightweightDataCleaningAgent

load_dotenv()


def show_mode_metric(df, column):
    """Show the mode(s) of a column; all tied modes are displayed."""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found in the cleaned data.")
        return
    modes = df[column].dropna().mode()
    if len(modes) == 0:
        st.metric(f"Mode of {column}", "No values")
        return
    st.metric(f"Mode of {column}", ", ".join(str(m) for m in modes.sort_values()))


def show_min_max_metrics(df, column):
    """Show the minimum and maximum of a numeric column."""
    if column not in df.columns:
        st.warning(f"Column '{column}' not found in the cleaned data.")
        return
    values = pd.to_numeric(df[column], errors="coerce")
    if values.notna().sum() == 0:
        st.warning(f"Column '{column}' has no valid numeric values.")
        return
    col_min, col_max = st.columns(2)
    col_min.metric(f"{column} (minimum)", f"{values.min():,.2f}")
    col_max.metric(f"{column} (maximum)", f"{values.max():,.2f}")
    ignored = int(values.isna().sum() - df[column].isna().sum())
    if ignored > 0:
        st.caption(f"{ignored} non-numeric value(s) in '{column}' were ignored.")


st.title("🧹 Data Cleaning Agent")

# Upload file
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

# Forget previous results when a different file is selected (or the file is removed)
current_file_id = (uploaded_file.name, uploaded_file.size) if uploaded_file else None
if st.session_state.get("file_id") != current_file_id:
    st.session_state["file_id"] = current_file_id
    st.session_state.pop("df_cleaned", None)
    st.session_state.pop("original_missing", None)

if uploaded_file:
    # Load data
    df_raw = pd.read_csv(uploaded_file)

    # Clean button
    if st.button("Clean Data"):
        with st.spinner("Cleaning..."):
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
            agent = LightweightDataCleaningAgent(model=llm, log=True)
            # Missing values per column of the original dataset, before any cleaning
            st.session_state["original_missing"] = df_raw.isna().sum()
            agent.invoke_agent(data_raw=df_raw)
            st.session_state["df_cleaned"] = agent.get_data_cleaned()

            st.success("Done!")

    if "df_cleaned" in st.session_state:
        df_cleaned = st.session_state["df_cleaned"]

        st.subheader("Cleaned Data")
        if "original_missing" in st.session_state:
            st.write("Original missing values per column (before cleaning):")
            st.dataframe(
                st.session_state["original_missing"].rename("Missing values").to_frame()
            )
        st.write(f"Shape: {df_cleaned.shape[0]} rows × {df_cleaned.shape[1]} columns")
        st.dataframe(df_cleaned.head())

        # Download
        csv = df_cleaned.to_csv(index=False)
        st.download_button(
            "Download Cleaned Data",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

        st.subheader("Basic metrics of Data cleaning")

        st.write("Additional metrics of the cleaning process")
        metrics_type = st.selectbox(
            "Select the type of variables",
            ["Non-numerical variables", "Numerical variables"],
            key="metrics_type",
        )
        if metrics_type == "Numerical variables":
            show_min_max_metrics(df_cleaned, "age")
            show_min_max_metrics(df_cleaned, "salary")
        else:
            show_mode_metric(df_cleaned, "department")
            show_mode_metric(df_cleaned, "city")
