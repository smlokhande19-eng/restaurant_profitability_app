import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Restaurant Profitability Analytics",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.markdown('<div class="main-header">🍽️ Restaurant Channel Profitability Analytics</div>', unsafe_allow_html=True)
    
    file_path = "SkyCity Auckland Restaurants & Bars.csv"
    df = load_data(file_path)
    
    if df is None:
        return
    
    st.success(f"✅ Data loaded: {len(df)} restaurants")
    
    # Simple overview metrics
    total_revenue = df[['InStoreRevenue','UberEatsRevenue','DoorDashRevenue','SelfDeliveryRevenue']].sum().sum()
    total_profit = df[['InStoreNetProfit','UberEatsNetProfit','DoorDashNetProfit','SelfDeliveryNetProfit']].sum().sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Revenue", f"${total_revenue:,.0f}")
    with col2:
        st.metric("Total Profit", f"${total_profit:,.0f}")
    with col3:
        margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        st.metric("Overall Margin", f"{margin:.1f}%")
    
    # Channel comparison bar chart
    channels = ['InStoreNetProfit', 'UberEatsNetProfit', 'DoorDashNetProfit', 'SelfDeliveryNetProfit']
    channel_names = ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery']
    
    channel_profits = [df[ch].sum() for ch in channels]
    
    fig = px.bar(
        x=channel_names, 
        y=channel_profits,
        title="Net Profit by Channel",
        labels={'x':'Channel', 'y':'Total Profit ($)'},
        text=[f'${p:,.0f}' for p in channel_profits]
    )
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()

