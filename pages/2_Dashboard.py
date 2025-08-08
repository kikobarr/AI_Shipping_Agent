import altair as alt
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from services.dashboardService import load_and_clean_data, split_by_category

st.set_page_config(page_title="Procurement Dashboard", layout="wide")

# Font & Style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 2rem;
    }

    .section {
        background-color: var(--background-color);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Procurement Dashboard</div>', unsafe_allow_html=True)

# File Upload Warning
st.warning("""
Please ensure your file:
- Is a `.csv` format.
- Has numeric fields for 'Goods (Amt)', 'Services (Amt)', etc.
- Includes proper headers and PO Date format.
""")

# Upload
uploaded_file = st.file_uploader("Upload your procurement data (.csv)", type=["csv"])

if uploaded_file:
    df = load_and_clean_data(uploaded_file)

    with st.container():
        st.subheader("Filter by Year")
        df['PO Date'] = pd.to_datetime(df['PO Date'], errors='coerce')
        years = sorted(df['PO Date'].dt.year.dropna().unique())
        year = st.selectbox("Select a year", ["All Years"] + [str(y) for y in years])

        if year != "All Years":
            df = df[df['PO Date'].dt.year == int(year)]
            st.success(f"Showing data for {year} with {len(df):,} records")
        else:
            st.info(f"Showing all data with {len(df):,} records")

    categories = split_by_category(df)

    with st.container():
        st.subheader("Total Spend by Category")
        amt_cols = ['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']
        totals = df[amt_cols].sum().reset_index()
        totals.columns = ["Category", "Total Spend"]
        totals["Category"] = totals["Category"].str.replace(" \\(Amt\\)", "", regex=True)
        totals["Percent"] = totals["Total Spend"] / totals["Total Spend"].sum() * 100

        st.dataframe(
            totals.style.format({"Total Spend": "${:,.2f}", "Percent": "{:.2f}%"}),
            use_container_width=True
        )

        pie = alt.Chart(totals).mark_arc(innerRadius=50).encode(
            theta="Total Spend:Q",
            color="Category:N",
            tooltip=["Category", alt.Tooltip("Total Spend:Q", format=",.2f"), alt.Tooltip("Percent:Q", format=".2f")]
        )
        st.altair_chart(pie, use_container_width=True)

        csv_data = totals.to_csv(index=False).encode("utf-8")
        st.download_button("Download Summary CSV", data=csv_data, file_name="summary.csv", mime="text/csv")

    with st.container():
        st.subheader("Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

    with st.container():
        st.subheader("Spend Breakdown by Line Count")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Goods", len(categories['goods']))
        col2.metric("Services", len(categories['services']))
        col3.metric("Construction", len(categories['construction']))
        col4.metric("IT", len(categories['it']))

    with st.container():
        st.subheader("Top Suppliers by Category")
        category = st.selectbox("Select Category", ["Goods", "Services", "Construction", "IT"])
        data = categories[category.lower()]
        if not data.empty:
            grouped = data.groupby("Supplier Name")[f"{category} (Amt)"].sum().reset_index()
            top10 = grouped.sort_values(by=f"{category} (Amt)", ascending=False).head(10)

            chart = alt.Chart(top10).mark_bar().encode(
                x=alt.X(f"{category} (Amt):Q", title="Amount ($)"),
                y=alt.Y("Supplier Name:N", sort='-x'),
                tooltip=["Supplier Name", f"{category} (Amt)"]
            ).properties(height=400, title=f"Top 10 Suppliers by {category}")

            st.altair_chart(chart, use_container_width=True)

            selected_supplier = st.selectbox("Select Supplier", top10["Supplier Name"])
            supplier_lines = data[data["Supplier Name"] == selected_supplier]
            st.dataframe(supplier_lines[["Line Descr", f"{category} (Amt)"]])
        else:
            st.info("No data available for selected category.")
