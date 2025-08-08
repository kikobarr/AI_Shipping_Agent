import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import random

st.set_page_config(page_title="Shipping Dashboard", layout="wide")

# Professional styling with high contrast accessibility
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-color);
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    .metric-card {
        background-color: #000000;
        color: #ffffff;
        border: 3px solid #ffffff;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        font-weight: 600;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #00ff00;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }

    .metric-label {
        color: #ffffff;
        font-size: 1rem;
        margin-top: 0.5rem;
        font-weight: 600;
    }

    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-color);
        margin: 2rem 0 1rem 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }
    
    /* Light mode high contrast */
    @media (prefers-color-scheme: light) {
        .metric-card {
            background-color: #ffffff;
            color: #000000;
            border: 3px solid #000000;
        }
        
        .metric-value {
            color: #008000;
        }
        
        .metric-label {
            color: #000000;
        }
    }
    
    /* Dark mode high contrast */
    @media (prefers-color-scheme: dark) {
        .metric-card {
            background-color: #000000;
            color: #ffffff;
            border: 3px solid #ffffff;
        }
        
        .metric-value {
            color: #00ff00;
        }
        
        .metric-label {
            color: #ffffff;
        }
    }
    
    /* High contrast buttons */
    .stButton > button {
        background-color: #000000 !important;
        color: #ffffff !important;
        border: 2px solid #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: 2px solid #000000 !important;
    }
    
    /* High contrast dataframes */
    .stDataFrame {
        border: 2px solid var(--text-color) !important;
    }
    
    /* High contrast text */
    .stMarkdown p, .stMarkdown li {
        font-weight: 500 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Shipping Dashboard</div>', unsafe_allow_html=True)

# Generate sample shipping data for demonstration
@st.cache_data
def generate_sample_data():
    """Generate sample shipping data for dashboard demonstration"""
    
    # Sample data for the last 30 days
    dates = [datetime.now() - timedelta(days=x) for x in range(30)]
    
    # Sample shipping data
    shipping_data = []
    for date in dates:
        # Generate 3-8 shipments per day
        daily_shipments = random.randint(3, 8)
        for _ in range(daily_shipments):
            shipping_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'service': random.choice(['FedEx Ground', 'FedEx Express Saver', 'FedEx 2Day', 'FedEx Standard Overnight', 'FedEx Priority Overnight']),
                'cost': round(random.uniform(15.0, 250.0), 2),
                'weight': round(random.uniform(1.0, 50.0), 1),
                'origin_state': random.choice(['CA', 'NY', 'TX', 'FL', 'IL']),
                'destination_state': random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'GA', 'WA', 'PA']),
                'status': random.choice(['Delivered', 'In Transit', 'Processing', 'Delivered', 'Delivered'])  # Bias toward delivered
            })
    
    return pd.DataFrame(shipping_data)

# Load sample data
df = generate_sample_data()
df['date'] = pd.to_datetime(df['date'])

# Key Metrics Section
st.markdown('<div class="section-header">📈 Key Metrics (Last 30 Days)</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_shipments = len(df)
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{total_shipments:,}</div>
        <div class="metric-label">Total Shipments</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    total_cost = df['cost'].sum()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${total_cost:,.0f}</div>
        <div class="metric-label">Total Shipping Cost</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_cost = df['cost'].mean()
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">${avg_cost:.2f}</div>
        <div class="metric-label">Average Cost per Shipment</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    delivered_rate = (df['status'] == 'Delivered').mean() * 100
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{delivered_rate:.1f}%</div>
        <div class="metric-label">Delivery Success Rate</div>
    </div>
    """, unsafe_allow_html=True)

# Daily Shipping Volume Chart
st.markdown('<div class="section-header">📦 Daily Shipping Volume</div>', unsafe_allow_html=True)

daily_volume = df.groupby('date').size().reset_index(name='shipments')
daily_cost = df.groupby('date')['cost'].sum().reset_index()
daily_stats = daily_volume.merge(daily_cost, on='date')

volume_chart = alt.Chart(daily_stats).mark_line(point=True, color='#3b82f6').encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('shipments:Q', title='Number of Shipments'),
    tooltip=['date:T', 'shipments:Q', alt.Tooltip('cost:Q', format='$.2f', title='Total Cost')]
).properties(
    height=300,
    title='Daily Shipment Volume'
)

st.altair_chart(volume_chart, use_container_width=True)

# Service Usage and Cost Analysis
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">🚚 Service Usage</div>', unsafe_allow_html=True)
    
    service_usage = df['service'].value_counts().reset_index()
    service_usage.columns = ['Service', 'Count']
    
    service_chart = alt.Chart(service_usage).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('Count:Q'),
        color=alt.Color('Service:N', scale=alt.Scale(scheme='category10')),
        tooltip=['Service:N', 'Count:Q']
    ).properties(
        height=300,
        title='FedEx Service Distribution'
    )
    
    st.altair_chart(service_chart, use_container_width=True)

with col2:
    st.markdown('<div class="section-header">💰 Cost by Service</div>', unsafe_allow_html=True)
    
    service_cost = df.groupby('service')['cost'].mean().reset_index()
    service_cost = service_cost.sort_values('cost', ascending=True)
    
    cost_chart = alt.Chart(service_cost).mark_bar(color='#10b981').encode(
        x=alt.X('cost:Q', title='Average Cost ($)'),
        y=alt.Y('service:N', sort='-x', title='Service'),
        tooltip=['service:N', alt.Tooltip('cost:Q', format='$.2f')]
    ).properties(
        height=300,
        title='Average Cost by Service'
    )
    
    st.altair_chart(cost_chart, use_container_width=True)

# Geographic Analysis
st.markdown('<div class="section-header">🗺️ Geographic Distribution</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Origin States")
    origin_stats = df['origin_state'].value_counts().head(5).reset_index()
    origin_stats.columns = ['State', 'Shipments']
    st.dataframe(origin_stats, use_container_width=True, hide_index=True)

with col2:
    st.subheader("Top Destination States")
    dest_stats = df['destination_state'].value_counts().head(5).reset_index()
    dest_stats.columns = ['State', 'Shipments']
    st.dataframe(dest_stats, use_container_width=True, hide_index=True)

# Recent Activity
st.markdown('<div class="section-header">📋 Recent Shipping Activity</div>', unsafe_allow_html=True)

recent_shipments = df.sort_values('date', ascending=False).head(10)
display_df = recent_shipments[['date', 'service', 'cost', 'weight', 'origin_state', 'destination_state', 'status']].copy()
display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
display_df.columns = ['Date', 'Service', 'Cost ($)', 'Weight (lbs)', 'Origin', 'Destination', 'Status']

st.dataframe(display_df, use_container_width=True, hide_index=True)

# Quick Actions
st.markdown('<div class="section-header">🚀 Quick Actions</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📦 Get New Quote", use_container_width=True):
        st.switch_page("pages/2_Shipping.py")

with col2:
    if st.button("🤖 Ask AI Assistant", use_container_width=True):
        st.switch_page("AI_Agent.py")

with col3:
    if st.button("📊 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Footer
st.markdown("---")
st.markdown("*Dashboard shows sample data for demonstration • Built with Streamlit*")
