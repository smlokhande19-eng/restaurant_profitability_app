import streamlit as st
import pandas as pd

def analyze_channel_profitability(df):
    channels = {
        'In-Store': ('InStoreRevenue', 'InStoreNetProfit', 'InStoreOrdersCount'),
        'Uber Eats': ('UberEatsRevenue', 'UberEatsNetProfit', 'UberEatsOrdersCount'),
        'DoorDash': ('DoorDashRevenue', 'DoorDashNetProfit', 'DoorDashOrdersCount'),
        'Self-Delivery': ('SelfDeliveryRevenue', 'SelfDeliveryNetProfit', 'SelfDeliveryOrdersCount')
    }
    
    results = {}
    
    for channel_name, (rev_col, profit_col, orders_col) in channels.items():
        total_revenue = df[rev_col].sum()
        total_profit = df[profit_col].sum()
        total_orders = df[orders_col].sum()
        
        margin_pct = (total_profit / total_revenue * 100) if total_revenue != 0 else 0
        profit_per_order = (total_profit / total_orders) if total_orders != 0 else 0
        
        results[channel_name] = {
            'Total Revenue': total_revenue,
            'Total Profit': total_profit,
            'Total Orders': total_orders,
            'Margin %': margin_pct,
            'Profit per Order': profit_per_order
        }
    
    return pd.DataFrame(results).T

# ---------------- STREAMLIT UI ---------------- #

if __name__ == '__main__':
    print('Module loaded successfully - no syntax errors')

def analyze_cost_components(df):
    # Calculate cost breakdown for each channel
    
    # In-Store costs
    df['InStore_COGS'] = df['InStoreRevenue'] * df['COGSRate']
    df['InStore_OPEX'] = df['InStoreRevenue'] * df['OPEXRate']
    
    # Uber Eats costs
    df['UberEats_COGS'] = df['UberEatsRevenue'] * df['COGSRate']
    df['UberEats_OPEX'] = df['UberEatsRevenue'] * df['OPEXRate']
    df['UberEats_Commission'] = df['UberEatsRevenue'] * df['CommissionRate']
    
    # DoorDash costs
    df['DoorDash_COGS'] = df['DoorDashRevenue'] * df['COGSRate']
    df['DoorDash_OPEX'] = df['DoorDashRevenue'] * df['OPEXRate']
    df['DoorDash_Commission'] = df['DoorDashRevenue'] * df['CommissionRate']
    
    # Self-Delivery costs
    df['SelfDelivery_COGS'] = df['SelfDeliveryRevenue'] * df['COGSRate']
    df['SelfDelivery_OPEX'] = df['SelfDeliveryRevenue'] * df['OPEXRate']
    df['SelfDelivery_DeliveryCost'] = df['SD_DeliveryTotalCost']
    
    return df
 
def create_profitability_comparison(df):
    # Create comparison chart
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Total profit by channel
    profits = [
        df['InStoreNetProfit'].sum(),
        df['UberEatsNetProfit'].sum(),
        df['DoorDashNetProfit'].sum(),
        df['SelfDeliveryNetProfit'].sum()
    ]
    
    channels = ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery']
    colors = ['#2E75B6', '#FF6B6B', '#4ECDC4', '#95E1D3']
    
    axes[0].bar(channels, profits, color=colors)
    axes[0].set_title('Total Profit by Channel', fontsize=14, weight='bold')
    axes[0].set_ylabel('Net Profit ($)')
    axes[0].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('profitability_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()
 
# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Page configuration
st.set_page_config(
    page_title='Restaurant Channel Profitability',
    page_icon='🍽️',
    layout='wide'
)

# Title and description
st.title('🍽️ Restaurant Delivery Channel Profitability Analysis')
st.markdown("""
Compare profitability across In-Store, Uber Eats, DoorDash, and Self-Delivery channels.
Analyze margin impact of commissions and delivery costs.
""")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('restaurant_data.csv')
    return df

df = load_data()
 
# Sidebar filters
st.sidebar.header('Filters')

# Cuisine filter
cuisines = ['All'] + sorted(df['CuisineType'].unique().tolist())
selected_cuisine = st.sidebar.selectbox('Select Cuisine', cuisines)

# Segment filter
segments = ['All'] + sorted(df['Segment'].unique().tolist())
selected_segment = st.sidebar.selectbox('Select Segment', segments)

# What-if analysis sliders
st.sidebar.header('What-If Analysis')
commission_adjustment = st.sidebar.slider(
    'Commission Rate Adjustment (%)',
    -10.0, 10.0, 0.0, 0.5
)

delivery_cost_adjustment = st.sidebar.slider(
    'Delivery Cost Adjustment (%)',
    -50.0, 50.0, 0.0, 5.0
)

# Filter dataframe
filtered_df = df.copy()
if selected_cuisine != 'All':
    filtered_df = filtered_df[filtered_df['CuisineType'] == selected_cuisine]
if selected_segment != 'All':
    filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]
 
# KPI Cards
st.header('Key Performance Indicators')

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_revenue = (
        filtered_df['InStoreRevenue'].sum() +
        filtered_df['UberEatsRevenue'].sum() +
        filtered_df['DoorDashRevenue'].sum() +
        filtered_df['SelfDeliveryRevenue'].sum()
    )
    st.metric('Total Revenue', f'${total_revenue:,.0f}')

with col2:
    total_profit = (
        filtered_df['InStoreNetProfit'].sum() +
        filtered_df['UberEatsNetProfit'].sum() +
        filtered_df['DoorDashNetProfit'].sum() +
        filtered_df['SelfDeliveryNetProfit'].sum()
    )
    st.metric('Total Net Profit', f'${total_profit:,.0f}')

with col3:
    overall_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    st.metric('Overall Margin', f'{overall_margin:.1f}%')

with col4:
    total_orders = (
        filtered_df['InStoreOrdersCount'].sum() +
        filtered_df['UberEatsOrdersCount'].sum() +
        filtered_df['DoorDashOrdersCount'].sum() +
        filtered_df['SelfDeliveryOrdersCount'].sum()
    )
    st.metric('Total Orders', f'{total_orders:,.0f}')
 
# Channel comparison chart
st.header('Channel Profitability Comparison')

channel_data = {
    'Channel': ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'],
    'Revenue': [
        filtered_df['InStoreRevenue'].sum(),
        filtered_df['UberEatsRevenue'].sum(),
        filtered_df['DoorDashRevenue'].sum(),
        filtered_df['SelfDeliveryRevenue'].sum()
    ],
    'Net Profit': [
        filtered_df['InStoreNetProfit'].sum(),
        filtered_df['UberEatsNetProfit'].sum(),
        filtered_df['DoorDashNetProfit'].sum(),
        filtered_df['SelfDeliveryNetProfit'].sum()
    ]
}

channel_df = pd.DataFrame(channel_data)
channel_df['Margin %'] = (channel_df['Net Profit'] / channel_df['Revenue'] * 100)

fig = make_subplots(
    rows=1, cols=2,
    subplot_titles=('Revenue vs Profit by Channel', 'Profit Margin by Channel')
)

fig.add_trace(
    go.Bar(x=channel_df['Channel'], y=channel_df['Revenue'], name='Revenue',
           marker_color='lightblue'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=channel_df['Channel'], y=channel_df['Net Profit'], name='Net Profit',
           marker_color='lightgreen'),
    row=1, col=1
)

fig.add_trace(
    go.Bar(x=channel_df['Channel'], y=channel_df['Margin %'],
           marker_color=['#2E75B6', '#FF6B6B', '#4ECDC4', '#95E1D3']),
    row=1, col=2
)

fig.update_layout(height=500, showlegend=True)
st.plotly_chart(fig, use_container_width=True)
 
