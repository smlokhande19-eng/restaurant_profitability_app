import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Load data function
@st.cache_data
def load_data(file_path):
    """Load and prepare restaurant data"""
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# Calculate KPIs
def calculate_kpis(df):
    """Calculate key performance indicators"""
    kpis = {}
    kpis['total_revenue'] = (df['InStoreRevenue'].sum() + df['UberEatsRevenue'].sum() + 
                             df['DoorDashRevenue'].sum() + df['SelfDeliveryRevenue'].sum())
    kpis['total_profit'] = (df['InStoreNetProfit'].sum() + df['UberEatsNetProfit'].sum() + 
                            df['DoorDashNetProfit'].sum() + df['SelfDeliveryNetProfit'].sum())
    channels = {
        'In-Store': {'orders': 'InStoreOrders', 'revenue': 'InStoreRevenue', 'profit': 'InStoreNetProfit'},
        'Uber Eats': {'orders': 'UberEatsOrders', 'revenue': 'UberEatsRevenue', 'profit': 'UberEatsNetProfit'},
        'DoorDash': {'orders': 'DoorDashOrders', 'revenue': 'DoorDashRevenue', 'profit': 'DoorDashNetProfit'},
        'Self-Delivery': {'orders': 'SelfDeliveryOrders', 'revenue': 'SelfDeliveryRevenue', 'profit': 'SelfDeliveryNetProfit'}
    }
    for channel_name, cols in channels.items():
        total_orders = df[cols['orders']].sum()
        total_revenue = df[cols['revenue']].sum()
        total_profit = df[cols['profit']].sum()
        kpis[f'{channel_name}_orders'] = total_orders
        kpis[f'{channel_name}_revenue'] = total_revenue
        kpis[f'{channel_name}_profit'] = total_profit
        kpis[f'{channel_name}_profit_per_order'] = total_profit / total_orders if total_orders > 0 else 0
        kpis[f'{channel_name}_margin'] = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    return kpis

# Main app
def main():
    st.set_page_config(
        page_title="Restaurant Profitability Analytics",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.markdown("""
    <style>
        /* Main App Background (Dark Navy) */
        .stApp {
            background-color: #021225;
            color: white;
        }
        
        /* Sidebar Background (Bright Blue) */
        [data-testid="stSidebar"] {
            background-color: #0084ba !important;
        }
        
        /* Sidebar text color overrides */
        [data-testid="stSidebar"] * {
            color: white !important;
        }

        .main-header {
            font-size: 3rem;
            font-weight: 900;
            color: white;
            text-align: center;
            margin: 1rem 0 1rem 0;
            padding-bottom: 5px;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: bold;
            color: white;
            margin-top: 2rem;
            margin-bottom: 1rem;
            border-bottom: 3px solid rgba(255, 255, 255, 0.2);
            padding-bottom: 0.5rem;
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.05);
            color: white;
            padding: 1.5rem;
            border-radius: 16px;
            border-left: 5px solid #0084ba;
            margin-bottom: 1rem;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
        }
        .insight-box {
            background-color: rgba(255, 255, 255, 0.08);
            color: white;
            padding: 1rem;
            border-radius: 12px;
            border-left: 4px solid #0084ba;
            margin: 1rem 0;
        }
        .stMarkdown {
            color: white;
        }
        /* Metric values and labels */
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            padding: 1rem 0.5rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        div[data-testid="stMetricValue"] {
            color: white;
        }
        div[data-testid="stMetricValue"] > div {
            font-size: 1.5rem !important;
            white-space: normal !important;
            word-break: break-all;
            line-height: 1.2;
        }
        div[data-testid="stMetricLabel"] {
            color: #cccccc;
            font-size: 1rem !important;
        }
        
        html, body, .stApp, .main, .block-container {
            overflow-x: hidden !important;
            overflow-y: auto !important;
            min-height: 100vh;
        }
        .stApp {
            overscroll-behavior: contain;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-header">Restaurant Sales & Profit Trends</div>', unsafe_allow_html=True)
    st.sidebar.title("Controls & Filters")
    file_path = "SkyCity Auckland Restaurants & Bars.csv"
    df = load_data(file_path)
    if df is None:
        st.error("Could not load data. Please check the file path.")
        st.info(f"Looking for file at: {file_path}")
        st.info("Tip: Make sure the CSV file exists at the specified location.")
        return
    st.sidebar.success(f"Data loaded: {len(df)} restaurants")
    st.sidebar.markdown("### Filters")
    cuisines = ['All'] + sorted(df['CuisineType'].unique().tolist())
    selected_cuisine = st.sidebar.selectbox("Cuisine Type", cuisines)
    segments = ['All'] + sorted(df['Segment'].unique().tolist())
    selected_segment = st.sidebar.selectbox("Business Segment", segments)
    subregions = ['All'] + sorted(df['Subregion'].unique().tolist())
    selected_subregion = st.sidebar.selectbox("Subregion", subregions)
    filtered_df = df.copy()
    if selected_cuisine != 'All':
        filtered_df = filtered_df[filtered_df['CuisineType'] == selected_cuisine]
    if selected_segment != 'All':
        filtered_df = filtered_df[filtered_df['Segment'] == selected_segment]
    if selected_subregion != 'All':
        filtered_df = filtered_df[filtered_df['Subregion'] == selected_subregion]
    st.sidebar.info(f"Filtered: {len(filtered_df)} restaurants")
    st.sidebar.markdown("### What-If Analysis")
    commission_adjustment = st.sidebar.slider(
        "Commission Rate Adjustment (%)",
        min_value=-50,
        max_value=50,
        value=0,
        step=5
    )
    delivery_cost_adjustment = st.sidebar.slider(
        "Delivery Cost Adjustment (%)",
        min_value=-50,
        max_value=50,
        value=0,
        step=5
    )
    if commission_adjustment != 0 or delivery_cost_adjustment != 0:
        filtered_df = filtered_df.copy()
        if commission_adjustment != 0:
            adj_factor = 1 + (commission_adjustment / 100)
            for channel in ['UberEats', 'DoorDash']:
                revenue_col = f'{channel}Revenue'
                profit_col = f'{channel}NetProfit'
                original_commission = filtered_df[revenue_col] * filtered_df['CommissionRate']
                new_commission = original_commission * adj_factor
                commission_diff = new_commission - original_commission
                filtered_df[profit_col] = filtered_df[profit_col] - commission_diff
        if delivery_cost_adjustment != 0:
            adj_factor = 1 + (delivery_cost_adjustment / 100)
            cost_diff = filtered_df['SD_DeliveryTotalCost'] * (adj_factor - 1)
            filtered_df['SelfDeliveryNetProfit'] = filtered_df['SelfDeliveryNetProfit'] - cost_diff
    kpis = calculate_kpis(filtered_df)
    tabs = [
        "Overview", 
        "Channel Comparison", 
        "Margin Analysis", 
        "Cost Breakdown",
        "Segment Analysis",
        "Risk Assessment"
    ]
    selected_tab = st.pills("Navigation", tabs, default="Overview", label_visibility="collapsed")
    if not selected_tab:
        selected_tab = "Overview"
    
    channel_map = {
        'In-Store': {'revenue': 'InStoreRevenue', 'profit': 'InStoreNetProfit'},
        'Uber Eats': {'revenue': 'UberEatsRevenue', 'profit': 'UberEatsNetProfit'},
        'DoorDash': {'revenue': 'DoorDashRevenue', 'profit': 'DoorDashNetProfit'},
        'Self-Delivery': {'revenue': 'SelfDeliveryRevenue', 'profit': 'SelfDeliveryNetProfit'}
    }
    
    if selected_tab == "Overview":
        st.markdown('<div class="section-header">Executive Summary</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Revenue ($)", f"{kpis['total_revenue']:,.0f}")
        with col2:
            st.metric("Total Profit ($)", f"{kpis['total_profit']:,.0f}")
        with col3:
            overall_margin = (kpis['total_profit'] / kpis['total_revenue'] * 100) if kpis['total_revenue'] else 0
            st.metric("Overall Margin (%)", f"{overall_margin:.1f}")
        with col4:
            st.metric("Restaurants", len(filtered_df))
            
        st.markdown("### **Net Profit by Channel - Big Overview**")
        st.markdown("---")

        # Big central diagram: Total Net Profit by Channel
        channel_profits_data = pd.DataFrame({
            'Channel': ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'],
            'Total Net Profit': [
                kpis['In-Store_profit'],
                kpis['Uber Eats_profit'],
                kpis['DoorDash_profit'],
                kpis['Self-Delivery_profit']
            ]
        })

        fig_big_profit = px.bar(
            channel_profits_data, 
            x='Channel', 
            y='Total Net Profit',
            title='**Total Net Profit by Channel**',
            color='Total Net Profit',
            color_continuous_scale='RdYlGn',
            text='Total Net Profit',
            height=600,
            template='plotly_white'
        )
        fig_big_profit.update_traces(
            texttemplate='$%{text:,.0f}', 
            textposition='outside',
            textfont_size=16
        )
        fig_big_profit.update_layout(
            showlegend=False,
            font_size=16,
            title_font_size=24,
            xaxis_title_font_size=18,
            yaxis_title_font_size=18,
            width=None,
            margin=dict(l=40, r=40, t=80, b=40)
        )
        st.plotly_chart(fig_big_profit, use_container_width=True)

        st.markdown("### Channel Distribution")
        col1, col2 = st.columns(2)
        with col1:
            channel_orders = pd.DataFrame({
                'Channel': ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'],
                'Orders': [
                    kpis['In-Store_orders'],
                    kpis['Uber Eats_orders'],
                    kpis['DoorDash_orders'],
                    kpis['Self-Delivery_orders']
                ]
            })
            fig = px.pie(channel_orders, values='Orders', names='Channel', title='Orders Distribution by Channel', color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=600,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=50, b=50, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            channel_revenue = pd.DataFrame({
                'Channel': ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'],
                'Revenue': [
                    kpis['In-Store_revenue'],
                    kpis['Uber Eats_revenue'],
                    kpis['DoorDash_revenue'],
                    kpis['Self-Delivery_revenue']
                ]
            })
            fig = px.pie(channel_revenue, values='Revenue', names='Channel', title='Revenue Distribution by Channel', color_discrete_sequence=px.colors.qualitative.Pastel)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                height=600,
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(t=50, b=50, l=20, r=20)
            )
            st.plotly_chart(fig, use_container_width=True)
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.markdown("#### Key Insights")
        channel_profits = {
            'In-Store': kpis['In-Store_profit'],
            'Uber Eats': kpis['Uber Eats_profit'],
            'DoorDash': kpis['DoorDash_profit'],
            'Self-Delivery': kpis['Self-Delivery_profit']
        }
        most_profitable = max(channel_profits, key=channel_profits.get)
        st.write(f"• **Most Profitable Channel**: {most_profitable} (${channel_profits[most_profitable]:,.0f} total profit)")
        st.write(f"• **Highest Margin Channel**: {most_profitable} ({kpis[f'{most_profitable}_margin']:.1f}% margin)")
        st.write(f"• **Total Orders**: {filtered_df['MonthlyOrders'].sum():,.0f} across all channels")
        st.markdown('</div>', unsafe_allow_html=True)
    elif selected_tab == "Channel Comparison":
        st.markdown('<div class="section-header">Channel Profitability Comparison</div>', unsafe_allow_html=True)
        st.markdown("### Net Profit by Channel")
        channel_data = pd.DataFrame({
            'Channel': ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'],
            'Total Profit': [
                kpis['In-Store_profit'],
                kpis['Uber Eats_profit'],
                kpis['DoorDash_profit'],
                kpis['Self-Delivery_profit']
            ],
            'Profit per Order': [
                kpis['In-Store_profit_per_order'],
                kpis['Uber Eats_profit_per_order'],
                kpis['DoorDash_profit_per_order'],
                kpis['Self-Delivery_profit_per_order']
            ],
            'Margin (%)': [
                kpis['In-Store_margin'],
                kpis['Uber Eats_margin'],
                kpis['DoorDash_margin'],
                kpis['Self-Delivery_margin']
            ]
        })
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(channel_data, x='Channel', y='Total Profit', title='Total Net Profit by Channel', color='Total Profit', color_continuous_scale='RdYlGn', text='Total Profit')
            fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width='stretch')
        with col2:
            fig = px.bar(channel_data, x='Channel', y='Profit per Order', title='Profit per Order by Channel', color='Profit per Order', color_continuous_scale='Viridis', text='Profit per Order')
            fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, width='stretch')
        st.markdown("### Profit Margin Comparison")
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Margin %', x=channel_data['Channel'], y=channel_data['Margin (%)'], text=channel_data['Margin (%)'].round(1), texttemplate='%{text}%', textposition='outside', marker_color=['#2ecc71', '#e74c3c', '#e67e22', '#3498db']))
        fig.update_layout(title='Profit Margin by Channel', yaxis_title='Margin (%)', showlegend=False, height=400)
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Detailed Channel Metrics")
        channel_data['Total Profit'] = channel_data['Total Profit'].apply(lambda x: f"${x:,.0f}")
        channel_data['Profit per Order'] = channel_data['Profit per Order'].apply(lambda x: f"${x:.2f}")
        channel_data['Margin (%)'] = channel_data['Margin (%)'].apply(lambda x: f"{x:.1f}%")
        st.dataframe(channel_data, use_container_width=True, hide_index=True)
    elif selected_tab == "Margin Analysis":
        st.markdown('<div class="section-header">Margin & Cost Analysis</div>', unsafe_allow_html=True)
        st.markdown("### Revenue to Profit Waterfall")
        selected_waterfall_channel = st.selectbox("Select Channel for Waterfall Analysis", ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'])
        channel_cols = channel_map[selected_waterfall_channel]
        total_revenue = filtered_df[channel_cols['revenue']].sum()
        total_profit = filtered_df[channel_cols['profit']].sum()
        cogs = (filtered_df[channel_cols['revenue']] * filtered_df['COGSRate']).sum()
        opex = (filtered_df[channel_cols['revenue']] * filtered_df['OPEXRate']).sum()
        if selected_waterfall_channel in ['Uber Eats', 'DoorDash']:
            commission = (filtered_df[channel_cols['revenue']] * filtered_df['CommissionRate']).sum()
            delivery_cost = 0
        else:
            commission = 0
            delivery_cost = filtered_df['SD_DeliveryTotalCost'].sum() if selected_waterfall_channel == 'Self-Delivery' else 0
        categories = ['Revenue', 'COGS', 'OPEX']
        values = [total_revenue, -cogs, -opex]
        if commission > 0:
            categories.append('Commission')
            values.append(-commission)
        if delivery_cost > 0:
            categories.append('Delivery Cost')
            values.append(-delivery_cost)
        categories.append('Net Profit')
        values.append(total_profit)
        fig = go.Figure(go.Waterfall(name="Waterfall", orientation="v", measure=["absolute"] + ["relative"] * (len(categories) - 2) + ["total"], x=categories, textposition="outside", text=[f"${v:,.0f}" for v in values], y=values, connector={"line": {"color": "rgb(63, 63, 63)"}}))
        fig.update_layout(title=f"{selected_waterfall_channel} - Revenue to Profit Breakdown", showlegend=False, height=500)
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Cost Structure Comparison")
        cost_structure_data = []
        for channel in ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery']:
            cols = channel_map[channel]
            rev = filtered_df[cols['revenue']].sum()
            if rev > 0:
                cogs_pct = (filtered_df[cols['revenue']] * filtered_df['COGSRate']).sum() / rev * 100
                opex_pct = (filtered_df[cols['revenue']] * filtered_df['OPEXRate']).sum() / rev * 100
                if channel in ['Uber Eats', 'DoorDash']:
                    commission_pct = (filtered_df[cols['revenue']] * filtered_df['CommissionRate']).sum() / rev * 100
                    other_pct = 0
                elif channel == 'Self-Delivery':
                    commission_pct = 0
                    other_pct = filtered_df['SD_DeliveryTotalCost'].sum() / rev * 100
                else:
                    commission_pct = 0
                    other_pct = 0
                profit_pct = filtered_df[cols['profit']].sum() / rev * 100
                cost_structure_data.append({'Channel': channel, 'COGS %': cogs_pct, 'OPEX %': opex_pct, 'Commission/Delivery %': commission_pct + other_pct, 'Net Profit %': profit_pct})
        cost_df = pd.DataFrame(cost_structure_data)
        fig = go.Figure()
        fig.add_trace(go.Bar(name='COGS %', x=cost_df['Channel'], y=cost_df['COGS %'], marker_color='#e74c3c'))
        fig.add_trace(go.Bar(name='OPEX %', x=cost_df['Channel'], y=cost_df['OPEX %'], marker_color='#e67e22'))
        fig.add_trace(go.Bar(name='Commission/Delivery %', x=cost_df['Channel'], y=cost_df['Commission/Delivery %'], marker_color='#95a5a6'))
        fig.add_trace(go.Bar(name='Net Profit %', x=cost_df['Channel'], y=cost_df['Net Profit %'], marker_color='#2ecc71'))
        fig.update_layout(barmode='stack', title='Cost Structure as % of Revenue', yaxis_title='% of Revenue', height=500)
        st.plotly_chart(fig, width='stretch')
    elif selected_tab == "Cost Breakdown":
        st.markdown('<div class="section-header">Detailed Cost Component Analysis</div>', unsafe_allow_html=True)
        st.markdown("### Commission Drag Analysis")
        commission_data = filtered_df[(filtered_df['UberEatsRevenue'] > 0) | (filtered_df['DoorDashRevenue'] > 0)].copy()
        commission_data['UberEatsCommission'] = commission_data['UberEatsRevenue'] * commission_data['CommissionRate']
        commission_data['DoorDashCommission'] = commission_data['DoorDashRevenue'] * commission_data['CommissionRate']
        commission_data['TotalCommission'] = commission_data['UberEatsCommission'] + commission_data['DoorDashCommission']
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Commission Paid", f"${commission_data['TotalCommission'].sum():,.0f}")
        with col2:
            delivery_revenue = filtered_df['UberEatsRevenue'].sum() + filtered_df['DoorDashRevenue'].sum()
            commission_rate_avg = (commission_data['TotalCommission'].sum() / delivery_revenue * 100) if delivery_revenue > 0 else 0
            st.metric("Average Commission Rate", f"{commission_rate_avg:.1f}%")
        commission_by_segment = commission_data.groupby('Segment').agg({'TotalCommission': 'sum', 'UberEatsRevenue': 'sum', 'DoorDashRevenue': 'sum'}).reset_index()
        commission_by_segment['CommissionRate'] = (commission_by_segment['TotalCommission'] / (commission_by_segment['UberEatsRevenue'] + commission_by_segment['DoorDashRevenue']) * 100)
        fig = px.bar(commission_by_segment, x='Segment', y='TotalCommission', title='Total Commission Paid by Segment', color='CommissionRate', color_continuous_scale='Reds', text='TotalCommission')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Self-Delivery Cost Analysis")
        delivery_data = filtered_df[filtered_df['SelfDeliveryOrders'] > 0].copy()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Self-Delivery Cost", f"${delivery_data['SD_DeliveryTotalCost'].sum():,.0f}")
        with col2:
            avg_cost_per_order = delivery_data['DeliveryCostPerOrder'].mean()
            st.metric("Average Cost per Delivery", f"${avg_cost_per_order:.2f}")
        delivery_by_cuisine = delivery_data.groupby('CuisineType').agg({'SD_DeliveryTotalCost': 'sum', 'SelfDeliveryOrders': 'sum', 'DeliveryCostPerOrder': 'mean'}).reset_index()
        delivery_by_cuisine = delivery_by_cuisine.sort_values('SD_DeliveryTotalCost', ascending=False).head(10)
        fig = px.bar(delivery_by_cuisine, x='CuisineType', y='SD_DeliveryTotalCost', title='Self-Delivery Costs by Cuisine (Top 10)', color='DeliveryCostPerOrder', color_continuous_scale='Blues', text='SD_DeliveryTotalCost')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Cost Efficiency Analysis")
        efficiency_data = filtered_df.copy()
        efficiency_data['TotalRevenue'] = (efficiency_data['InStoreRevenue'] + efficiency_data['UberEatsRevenue'] + efficiency_data['DoorDashRevenue'] + efficiency_data['SelfDeliveryRevenue'])
        efficiency_data['TotalProfit'] = (efficiency_data['InStoreNetProfit'] + efficiency_data['UberEatsNetProfit'] + efficiency_data['DoorDashNetProfit'] + efficiency_data['SelfDeliveryNetProfit'])
        efficiency_data['MarginPct'] = (efficiency_data['TotalProfit'] / efficiency_data['TotalRevenue'] * 100)
        fig = px.scatter(efficiency_data, x='TotalRevenue', y='MarginPct', color='Segment', size='MonthlyOrders', hover_data=['RestaurantName', 'CuisineType'], title='Revenue vs Margin % by Restaurant', labels={'TotalRevenue': 'Total Revenue ($)', 'MarginPct': 'Profit Margin (%)'})
        st.plotly_chart(fig, width='stretch')
    elif selected_tab == "Segment Analysis":
        st.markdown('<div class="section-header">Cuisine & Segment Profitability</div>', unsafe_allow_html=True)
        st.markdown("### Profitability Heatmap: Cuisine vs Segment")
        heatmap_channel = st.selectbox("Select Channel for Heatmap", ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'], key='heatmap_channel')
        channel_profit_col = channel_map[heatmap_channel]['profit']
        channel_revenue_col = channel_map[heatmap_channel]['revenue']
        heatmap_data = filtered_df.groupby(['CuisineType', 'Segment']).agg({channel_revenue_col: 'sum', channel_profit_col: 'sum'}).reset_index()
        heatmap_data['Margin'] = (heatmap_data[channel_profit_col] / heatmap_data[channel_revenue_col] * 100).fillna(0)
        pivot_margin = heatmap_data.pivot(index='CuisineType', columns='Segment', values='Margin')
        fig = go.Figure(data=go.Heatmap(z=pivot_margin.values, x=pivot_margin.columns, y=pivot_margin.index, colorscale='RdYlGn', text=pivot_margin.values.round(1), texttemplate='%{text}%', textfont={"size": 10}, colorbar=dict(title="Margin %")))
        fig.update_layout(title=f'{heatmap_channel} - Profit Margin by Cuisine & Segment', xaxis_title='Segment', yaxis_title='Cuisine Type', height=600)
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Top & Bottom Performers")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top 5 Most Profitable")
            top_performers = filtered_df.copy()
            top_performers['TotalProfit'] = (top_performers['InStoreNetProfit'] + top_performers['UberEatsNetProfit'] + top_performers['DoorDashNetProfit'] + top_performers['SelfDeliveryNetProfit'])
            top_5 = top_performers.nlargest(5, 'TotalProfit')[['RestaurantName', 'CuisineType', 'Segment', 'TotalProfit']]
            top_5['TotalProfit'] = top_5['TotalProfit'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(top_5, use_container_width=True, hide_index=True)
        with col2:
            st.markdown("#### Bottom 5 (Lowest Profit)")
            bottom_5 = top_performers.nsmallest(5, 'TotalProfit')[['RestaurantName', 'CuisineType', 'Segment', 'TotalProfit']]
            bottom_5['TotalProfit'] = bottom_5['TotalProfit'].apply(lambda x: f"${x:,.0f}")
            st.dataframe(bottom_5, use_container_width=True, hide_index=True)
        st.markdown("### Channel Performance by Segment")
        segment_analysis = []
        for segment in filtered_df['Segment'].unique():
            segment_df = filtered_df[filtered_df['Segment'] == segment]
            for channel in ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery']:
                cols = channel_map[channel]
                total_profit = segment_df[cols['profit']].sum()
                total_revenue = segment_df[cols['revenue']].sum()
                margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
                segment_analysis.append({'Segment': segment, 'Channel': channel, 'Profit': total_profit, 'Margin': margin})
        segment_df = pd.DataFrame(segment_analysis)
        fig = px.bar(segment_df, x='Segment', y='Profit', color='Channel', barmode='group', title='Profit by Segment & Channel', text='Profit')
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    elif selected_tab == "Risk Assessment":
        st.markdown('<div class="section-header">Profit Volatility & Risk Assessment</div>', unsafe_allow_html=True)
        st.markdown("### Channel Profitability Distribution")
        risk_channel = st.selectbox("Select Channel for Risk Analysis", ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery'], key='risk_channel')
        risk_profit_col = channel_map[risk_channel]['profit']
        fig = px.histogram(filtered_df, x=risk_profit_col, title=f'{risk_channel} - Profit Distribution', labels={risk_profit_col: 'Net Profit ($)'}, nbins=30, marginal='box')
        fig.add_vline(x=filtered_df[risk_profit_col].mean(), line_dash="dash", line_color="red", annotation_text="Mean")
        st.plotly_chart(fig, width='stretch')
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            mean_profit = filtered_df[risk_profit_col].mean()
            st.metric("Mean Profit", f"${mean_profit:,.0f}")
        with col2:
            std_profit = filtered_df[risk_profit_col].std()
            st.metric("Std Deviation", f"${std_profit:,.0f}")
        with col3:
            cv = (std_profit / mean_profit * 100) if mean_profit != 0 else 0
            st.metric("Volatility (CV)", f"{cv:.1f}%")
        with col4:
            loss_count = len(filtered_df[filtered_df[risk_profit_col] < 0])
            loss_pct = (loss_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
            st.metric("Loss-Making %", f"{loss_pct:.1f}%")
        st.markdown("### Risk Profile by Cuisine")
        risk_by_cuisine = []
        for cuisine in filtered_df['CuisineType'].unique():
            cuisine_df = filtered_df[filtered_df['CuisineType'] == cuisine]
            mean_val = cuisine_df[risk_profit_col].mean()
            std_val = cuisine_df[risk_profit_col].std()
            cv_val = (std_val / mean_val * 100) if mean_val != 0 else 0
            risk_by_cuisine.append({'Cuisine': cuisine, 'Mean Profit': mean_val, 'Volatility': cv_val, 'Count': len(cuisine_df)})
        risk_cuisine_df = pd.DataFrame(risk_by_cuisine).sort_values('Volatility', ascending=False)
        fig = px.scatter(risk_cuisine_df, x='Mean Profit', y='Volatility', size='Count', color='Cuisine', title=f'{risk_channel} - Risk-Return Profile by Cuisine', labels={'Mean Profit': 'Average Profit ($)', 'Volatility': 'Volatility (CV %)'}, hover_data=['Count'])
        st.plotly_chart(fig, width='stretch')
        st.markdown("### Loss-Prone Restaurants")
        loss_data = filtered_df.copy()
        loss_data['LossChannels'] = 0
        for channel in ['In-Store', 'Uber Eats', 'DoorDash', 'Self-Delivery']:
            profit_col = channel_map[channel]['profit']
            loss_data['LossChannels'] += (loss_data[profit_col] < 0).astype(int)
        high_risk = loss_data[loss_data['LossChannels'] >= 2].copy()
        if len(high_risk) > 0:
            high_risk['TotalProfit'] = (high_risk['InStoreNetProfit'] + high_risk['UberEatsNetProfit'] + high_risk['DoorDashNetProfit'] + high_risk['SelfDeliveryNetProfit'])
            high_risk_display = high_risk.nsmallest(10, 'TotalProfit')[['RestaurantName', 'CuisineType', 'Segment', 'LossChannels', 'TotalProfit']].copy()
            high_risk_display['TotalProfit'] = high_risk_display['TotalProfit'].apply(lambda x: f"${x:,.0f}")
            high_risk_display.columns = ['Restaurant', 'Cuisine', 'Segment', 'Loss-Making Channels', 'Total Profit']
            st.dataframe(high_risk_display, use_container_width=True, hide_index=True)
            st.warning(f"{len(high_risk)} restaurants have losses in 2 or more channels")
        else:
            st.success("No restaurants with losses in multiple channels")

if __name__ == "__main__":
    main()
