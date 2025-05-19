import streamlit as st
import pandas as pd
import os
import requests
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="ZSE Financial Dashboard", layout="wide")

company_list = sorted([d for d in os.listdir("data") if os.path.isdir(os.path.join("data", d))])
currency = st.sidebar.radio("Select Currency", ["ZWL", "USD"])
exchange_rate = 6104

@st.cache_data
def load_csv(company, filename_base):
    filename = f"{filename_base}_{currency.lower()}.csv"
    path = os.path.join("data", company, filename)
    if os.path.exists(path):
        try:
            df = pd.read_csv(path, index_col=0)
            df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
            return df
        except Exception as e:
            st.error(f"Error loading {filename}: {e}")
    return pd.DataFrame()

@st.cache_data
def fetch_zse_price_sheet():
    url = "https://www.zse.co.zw/price-sheet/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"width": "655"})
    rows = table.find_all("tr")
    data = []
    for row in rows:
        cols = [td.get_text(strip=True).replace(u'\xa0', '') for td in row.find_all("td")]
        if len(cols) == 4 and all(col != '' for col in cols):
            company, opening, closing, volume = cols
            try:
                data.append({
                    "Company": company,
                    "Opening Price": float(opening),
                    "Closing Price": float(closing),
                    "Traded Volume": int(float(volume))
                })
            except ValueError:
                continue
    return pd.DataFrame(data)

def format_percentages(df):
    df = df.copy()
    mask = df.index.to_series().str.contains("growth|margin", case=False, na=False)
    for col in df.columns:
        df.loc[mask, col] = pd.to_numeric(df.loc[mask, col], errors="coerce")
        df.loc[mask, col] = df.loc[mask, col].map(lambda x: f"{x:.2%}" if pd.notnull(x) else "")
    return df

def show_df(df):
    if df.empty:
        st.warning("No data available for this section.")
    else:
        styled_df = format_percentages(df)
        st.dataframe(styled_df, use_container_width=True)

selected_company = st.sidebar.selectbox("Select Company", company_list)
section = st.sidebar.selectbox("Section", [
    "Company Profile", "Financial Summary", "Income Statement", "Financial Position",
    "Cash Flow Statement", "Valuation Metrics", "Daily Price"
])

# Company Overview Panel
st.markdown("### Company Overview")
sector = "N/A"
price = "N/A"
market_cap = "N/A"
shares = None
profile_path = os.path.join("data", selected_company, "profile.txt")
if os.path.exists(profile_path):
    with open(profile_path, encoding="utf-8") as f:
        for line in f:
            if line.lower().startswith("sector:"):
                sector = line.strip().split(":", 1)[1].strip()
            if "Shares Outstanding" in line:
                try:
                    match = re.search(r"Shares Outstanding:\s*([\d,]+)", line)
                    if match:
                        shares_text = match.group(1)
                        shares = int(shares_text.replace(",", ""))
                except:
                    pass
prices = fetch_zse_price_sheet()
price_row = prices[prices["Company"].str.contains(selected_company.split()[0], case=False)]
if not price_row.empty:
    price = price_row.iloc[0]["Closing Price"] / 100  # Convert from cents
    if currency == "USD":
        price = price / exchange_rate
    if shares:
        market_cap = price * shares
col1, col2, col3, col4 = st.columns(4)
col1.metric("Company", selected_company)
col2.metric("Sector", sector)
col3.metric("Price", f"{price:,.2f} {currency}" if isinstance(price, (int, float)) else "N/A")
col4.metric("Market Cap", f"{market_cap:,.0f} {currency}" if isinstance(market_cap, (int, float)) else "N/A")

# Main section logic
if section == "Income Statement":
    df = load_csv(selected_company, "income_statement")
    show_df(df)

elif section == "Financial Position":
    df = load_csv(selected_company, "financial_position")
    show_df(df)

elif section == "Cash Flow Statement":
    df = load_csv(selected_company, "cash_flow_statement")
    show_df(df)

elif section == "Financial Summary":
    df = load_csv(selected_company, "financial_summary")
    show_df(df)

elif section == "Company Profile":
    if os.path.exists(profile_path):
        with open(profile_path, encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                if line.strip():
                    st.markdown(f"**{line.strip()}**")
    else:
        st.warning("No profile available.")

elif section == "Valuation Metrics":
    df = load_csv(selected_company, "income_statement")
    if "Net Profit" not in df.index:
        st.warning("Net Profit not found in income statement.")
    else:
        try:
            net_profit = pd.to_numeric(df.loc["Net Profit"], errors="coerce").dropna().iloc[-1]
        except Exception as e:
            st.error(f"Error reading Net Profit: {e}")
            net_profit = None
        if shares and net_profit:
            eps = net_profit / shares
            if isinstance(price, (int, float)):
                pe = price / eps if eps else None
                market_cap = price * shares
                st.metric("EPS", f"{eps:,.4f} {currency}")
                st.metric("P/E Ratio", f"{pe:.2f}" if pe else "N/A")
                st.metric("Market Capitalization", f"{market_cap:,.0f} {currency}")

elif section == "Daily Price":
    st.header("ZSE Daily Price Sheet")
    df = fetch_zse_price_sheet()
    if df.empty:
        st.warning("Price data not available.")
    else:
        if currency == "USD":
            df["Opening Price"] = df["Opening Price"] / (100 * exchange_rate)
            df["Closing Price"] = df["Closing Price"] / (100 * exchange_rate)
        else:
            df["Opening Price"] = df["Opening Price"] / 100
            df["Closing Price"] = df["Closing Price"] / 100
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download as CSV",
            df.to_csv(index=False).encode("utf-8"),
            file_name="zse_daily_prices.csv",
            mime="text/csv"
        )








































