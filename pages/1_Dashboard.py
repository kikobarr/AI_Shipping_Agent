# import streamlit as st
# import pandas as pd
# import altair as alt
# from services.dashboardService import (
#     save_uploaded_file,
#     load_and_clean_data,
#     split_by_category,
#     summarize_by_supplier_type,
#     melt_category_spend,
# )

# st.set_page_config(page_title="Diverse Supplier Dashboard", layout="wide")

# # Sophisticated UI Styling
# st.markdown("""
# <style>
#     @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

#     html, body, [class*="css"] {
#         font-family: 'Inter', sans-serif;
#         background-color: #f3f4f6;
#     }

#     .main-title {
#         font-size: 3rem;
#         font-weight: 700;
#         color: #1e293b;
#         margin-bottom: 2rem;
#     }

#     .section {
#         background-color: #ffffff;
#         padding: 2rem;
#         border-radius: 16px;
#         margin-bottom: 2rem;
#         box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 4px 6px rgba(0,0,0,0.05);
#         border: 1px solid #e5e7eb;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown('<div class="main-title">Diverse Supplier Procurement Dashboard</div>', unsafe_allow_html=True)

# # File upload
# uploaded_file = st.file_uploader("Upload your procurement data (.csv or .xlsx)", type=["csv", "xlsx"])
# if uploaded_file:
#     save_uploaded_file(uploaded_file)
#     st.cache_data.clear()
#     st.success("File uploaded successfully. Dashboard will reload.")

# @st.cache_data(ttl=3600)
# def get_data():
#     return load_and_clean_data()

# try:
#     df = get_data()
# except Exception as e:
#     st.error(f"Failed to load data: {e}")
#     st.stop()

# # Year filter
# st.markdown('<div class="section">', unsafe_allow_html=True)
# st.subheader("Filter by Year")
# df['PO Date'] = pd.to_datetime(df['PO Date'], errors='coerce')
# available_years = sorted(df['PO Date'].dt.year.dropna().unique())
# year_options = ["All Years"] + [str(y) for y in available_years]
# selected_year = st.selectbox("Select a year to analyze", year_options)

# if selected_year != "All Years":
#     df = df[df['PO Date'].dt.year == int(selected_year)]
#     st.success(f"Showing data for {selected_year} ({len(df):,} rows)")
# else:
#     st.info(f"Showing all data ({len(df):,} rows)")
# st.markdown('</div>', unsafe_allow_html=True)

# # Category Splits
# categories = split_by_category(df)
# totals = df[['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']].sum().reset_index()
# totals.columns = ["Category", "Amount"]
# totals["Category"] = totals["Category"].str.replace(" \\(Amt\\)", "", regex=True)
# totals["Percent"] = totals["Amount"] / totals["Amount"].sum() * 100

# # Two-column layout
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.markdown('<div class="section">', unsafe_allow_html=True)
#     st.subheader("Category Spend Distribution")
#     pie_chart = alt.Chart(totals).mark_arc(innerRadius=50).encode(
#         theta="Amount:Q",
#         color=alt.Color("Category:N", scale=alt.Scale(scheme="category10")),
#         tooltip=["Category", alt.Tooltip("Amount:Q", format=",.2f"), alt.Tooltip("Percent:Q", format=".2f")]
#     ).properties(height=400)
#     st.altair_chart(pie_chart, use_container_width=True)
#     st.markdown('</div>', unsafe_allow_html=True)

# with col2:
#     st.markdown('<div class="section">', unsafe_allow_html=True)
#     st.subheader("Summary Metrics")
#     col_a, col_b = st.columns(2)
#     col_a.metric("Total Goods", f"${totals.loc[0, 'Amount']:,.2f}")
#     col_a.metric("Total Services", f"${totals.loc[1, 'Amount']:,.2f}")
#     col_b.metric("Total Construction", f"${totals.loc[2, 'Amount']:,.2f}")
#     col_b.metric("Total IT", f"${totals.loc[3, 'Amount']:,.2f}")
#     st.markdown('</div>', unsafe_allow_html=True)

# # Diversity Summary Section
# st.markdown('<div class="section">', unsafe_allow_html=True)
# st.subheader("Supplier Diversity Overview")

# summary = summarize_by_supplier_type(df)
# st.dataframe(summary.style.format({
#     "Total_Spend": "${:,.2f}",
#     "Percent of Total": "{:.2f}%"
# }), use_container_width=True)

# melted = melt_category_spend(df)
# grouped = melted.groupby(["Supplier Type", "Category"])["Amount"].sum().reset_index()

# diversity_bar = alt.Chart(grouped).mark_bar().encode(
#     x="Amount:Q",
#     y=alt.Y("Supplier Type:N", sort='-x'),
#     color="Category:N",
#     tooltip=["Supplier Type", "Category", alt.Tooltip("Amount:Q", format=",.2f")]
# ).properties(height=400, title="Spend Breakdown by Supplier Type & Category")

# st.altair_chart(diversity_bar, use_container_width=True)
# st.markdown('</div>', unsafe_allow_html=True)
# pages/1_Dashboard.py

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

    with st.container():
        st.subheader("Forecast Future Spend (Prophet)")

        selected_forecast_cat = st.selectbox("Choose a category to forecast", amt_cols)
        forecast_df = df[["PO Date", selected_forecast_cat]].copy()
        forecast_df = forecast_df.groupby(pd.Grouper(key="PO Date", freq="MS")).sum().reset_index()
        forecast_df.columns = ["ds", "y"]

        try:
            from prophet import Prophet
            model = Prophet()
            model.fit(forecast_df)
            future = model.make_future_dataframe(periods=6, freq='MS')
            forecast = model.predict(future)

            fig = model.plot(forecast)
            plt.title(f"Forecast: {selected_forecast_cat}", fontsize=14)
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Forecasting failed: {e}")