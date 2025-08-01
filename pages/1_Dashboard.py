import altair as alt
import streamlit as st
from services.dashboardService import load_and_clean_data, split_by_category

st.set_page_config(page_title="Procurement Dashboard", layout="wide")

# Font & Style Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 2.5rem;
        color: #1f2937;
        margin-bottom: 1.5rem;
    }

    .dashboard-section {
        background-color: #f9fafb;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid #e5e7eb;
    }

    .metric-title {
        font-weight: 600;
        font-size: 1.25rem;
        color: #374151;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Page Title
st.markdown('<h2 class="main-title">Procurement Dashboard</h2>', unsafe_allow_html=True)

# Upload File
uploaded_file = st.file_uploader("Upload your procurement data (.csv)", type=["csv"])

if uploaded_file:
    df = load_and_clean_data(uploaded_file)
    categories = split_by_category(df)

    with st.container():
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("📊 Total Spend by Category")

        amount_cols = ['Goods (Amt)', 'Services (Amt)', 'Construction (Amt)', 'IT (Amt)']
        category_totals = df[amount_cols].sum().reset_index()
        category_totals.columns = ["Category", "Total Spend Amount"]
        category_totals["Category"] = category_totals["Category"].str.replace(" \\(Amt\\)", "", regex=True)
        category_totals["Total Spend Amount"] = category_totals["Total Spend Amount"].apply(lambda x: f"${x:,.2f}")
        st.dataframe(category_totals, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("🔍 Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("📦 Spend Breakdown by Category - Unique Line Descriptions")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Goods", len(categories['goods']))
        col2.metric("Services", len(categories['services']))
        col3.metric("Construction", len(categories['construction']))
        col4.metric("IT", len(categories['it']))
        st.markdown('</div>', unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dashboard-section">', unsafe_allow_html=True)
        st.subheader("🏢 Spend by Supplier")

        category_choice = st.selectbox("Select a category to visualize supplier spend", ["Goods", "Services", "Construction", "IT"])
        
        category_map = {
            "Goods": categories['goods'],
            "Services": categories['services'],
            "Construction": categories['construction'],
            "IT": categories['it']
        }

        selected_df = category_map[category_choice]

        if not selected_df.empty:
            chart_df = selected_df.groupby("Supplier Name")[f"{category_choice} (Amt)"].sum().reset_index()
            chart_df = chart_df.sort_values(by=f"{category_choice} (Amt)", ascending=False).head(10)

            bar_chart = alt.Chart(chart_df).mark_bar().encode(
                x=alt.X(f"{category_choice} (Amt):Q", title="Amount ($)"),
                y=alt.Y("Supplier Name:N", sort='-x', title="Supplier"),
                tooltip=["Supplier Name", f"{category_choice} (Amt)"]
            ).properties(
                width=700,
                height=400,
                title=f"Top Suppliers by {category_choice} Spend"
            )

            st.altair_chart(bar_chart, use_container_width=True)

            st.subheader("🧾 Detailed Line Items for Selected Supplier")
            top_suppliers = chart_df["Supplier Name"].tolist()
            selected_supplier = st.selectbox("Choose a top supplier", top_suppliers)
            supplier_lines = selected_df[selected_df["Supplier Name"] == selected_supplier]
            line_detail_df = supplier_lines[["Line Descr", f"{category_choice} (Amt)"]].sort_values(by=f"{category_choice} (Amt)", ascending=False)
            st.dataframe(line_detail_df.reset_index(drop=True), use_container_width=True)
        else:
            st.info("No data available for the selected category.")

        st.markdown('</div>', unsafe_allow_html=True)