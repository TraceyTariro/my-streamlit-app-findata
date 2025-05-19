import streamlit as st
import pandas as pd

st.set_page_config(page_title="ZSE Financial Dashboard", layout="wide")

# Sidebar navigation
section = st.sidebar.selectbox(
    "Navigate to",
    ("Financial Summary", "Income Statement", "Financial Position", "Cash Flow Statement", "Financial Ratios", "Daily Price")
)

@st.cache_data
def load_csv(file):
    df = pd.read_csv(file)
    df = df.loc[:, ~df.columns.str.contains("Unnamed")]
    return df

if section == "Financial Summary":
    st.title("Financial Summary")
    st.markdown("Overview of revenue, profit, EPS, and more.")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\financial_summary.csv")
    summary = df.loc[["Revenue", "Net Profit", "EPS"]]
    st.dataframe(summary.fillna("-"))

elif section == "Income Statement":
    st.title("Income Statement")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\income_statement.csv")
    st.dataframe(df.fillna("-"), use_container_width=True)

elif section == "Financial Position":
    st.title("Statement of Financial Position")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\financial_position.csv")
    st.dataframe(df.fillna("-"), use_container_width=True)

elif section == "Cash Flow Statement":
    st.title("Cash Flow Statement")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\cashflow_statement.csv")
    st.dataframe(df.fillna("-"), use_container_width=True)

elif section == "Financial Ratios":
    st.title("Financial Ratios")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\ratios.csv")
    st.dataframe(df.fillna("-"), use_container_width=True)

elif section == "Daily Price":
    st.title("Daily Price Tracker")
    df = load_csv(r"C:\Users\trace\OneDrive\Documents\Fordsworth Work\Findata\bat_zimbabwe\prices.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")
    st.line_chart(df.set_index("Date")["Price"])
    st.dataframe(df.tail(10))


