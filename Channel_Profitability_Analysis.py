import streamlit as st
import pandas as pd

# Your function
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

st.title("📊 Restaurant Channel Profitability Dashboard")

# File upload option
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    st.subheader("📁 Raw Data")
    st.write(df.head())
    
    result = analyze_channel_profitability(df)
    
    st.subheader("📊 Channel Profitability")
    st.dataframe(result)
    
    # Simple chart
    st.subheader("📈 Profit Comparison")
    st.bar_chart(result["Total Profit"])

else:
    st.info("Please upload a CSV file to proceed.")