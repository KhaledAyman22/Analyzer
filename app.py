import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from analyzer import analyze_trades, filter_trades_by_date, filter_trades_by_symbol, analyze_current_holdings
from datetime import datetime, timedelta

st.set_page_config(page_title="Trade Analyzer Pro", layout="wide", page_icon="📊")

# Custom CSS for better styling (Preserved)
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .positive { color: #00cc00; }
    .negative { color: #ff3333; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { padding: 10px 20px; }
</style>
""", unsafe_allow_html=True)

st.title("📊 Trading Performance Analyzer Pro")
st.markdown("Upload your IBKR trade CSV to get comprehensive insights into your trading performance.")

uploaded_file = st.file_uploader("📁 Upload IBKR Trade CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Date range filter
    df_temp = df.copy()
    df_temp['TradeDate'] = pd.to_datetime(df_temp['TradeDate'], errors='coerce')
    
    # Handle potential empty date range
    if not df_temp['TradeDate'].dropna().empty:
        min_date = df_temp['TradeDate'].min().date()
        max_date = df_temp['TradeDate'].max().date()
    else:
        min_date = datetime.now().date()
        max_date = datetime.now().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Symbol filter
    if 'Symbol' in df.columns:
        all_symbols = sorted(df['Symbol'].dropna().unique())
        selected_symbols = st.sidebar.multiselect(
            "Symbols",
            options=all_symbols,
            default=all_symbols
        )
    else:
        selected_symbols = []
    
    # Apply filters
    df_filtered = df.copy()
    if len(date_range) == 2:
        df_filtered = filter_trades_by_date(df_filtered, date_range[0], date_range[1])
    if selected_symbols:
        df_filtered = filter_trades_by_symbol(df_filtered, selected_symbols)
    
    # Analyze trades
    results = analyze_trades(df_filtered)
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Overview", 
        "📈 Performance", 
        "🎯 Symbol Analysis", 
        "📅 Time Analysis",
        "🏆 Best/Worst Trades",
        "💼 Holdings Dashboard",
        "📄 Raw Data"
    ])
    
    # ========== TAB 1: OVERVIEW ==========
    with tab1:
        st.header("Performance Overview")
        
        # Key metrics in columns
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Closed Trades", f"{results['total_trades']:,}")
            st.metric("Wins", f"{results['num_wins']:,}", delta=f"{results['win_rate']:.1f}%")
        
        with col2:
            st.metric("Win Rate", f"{results['win_rate']:.1f}%")
            st.metric("Losses", f"{results['num_losses']:,}")
        
        with col3:
            pnl_delta = "+" if results['total_pnl_net'] > 0 else ""
            st.metric(
                "Net P/L", 
                f"${results['total_pnl_net']:,.2f}",
                delta=f"{pnl_delta}{results['total_pnl_net']:,.2f}",
                help="Includes all commissions from buys and sells"
            )
        
        with col4:
            st.metric("Total Fees", f"${results['total_fees']:,.2f}")
            st.metric("Fee Impact", f"{results['commission_pct']:.1f}%")
        
        with col5:
            pf_display = "∞" if results['profit_factor'] == float('inf') else f"{results['profit_factor']:.2f}"
            st.metric("Profit Factor", pf_display)
            st.metric("Expectancy", f"${results['expectancy']:.2f}")
        
        st.divider()
        
        # Advanced metrics
        st.subheader("📊 Advanced Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Avg Win", f"${results['avg_win']:.2f}")
            st.metric("Avg Loss", f"${results['avg_loss']:.2f}")
        
        with col2:
            st.metric("R/R Ratio", f"{results['avg_rr_ratio']:.2f}:1")
            st.metric("Largest Win", f"${results['largest_win']:.2f}")
        
        with col3:
            st.metric("Max Drawdown", f"${results['max_drawdown']:.2f}")
            st.metric("Max DD %", f"{results['max_drawdown_pct']:.1f}%")
        
        with col4:
            st.metric("Win Streak", f"{results['max_win_streak']} trades")
            st.metric("Loss Streak", f"{results['max_loss_streak']} trades")
        
        st.divider()
        
        # Insights
        st.subheader("🧠 Key Insights")
        for insight in results['insights']:
            if "✅" in insight:
                st.success(insight)
            elif "🚨" in insight:
                st.error(insight)
            else:
                st.warning(insight)
    
    # ========== TAB 2: PERFORMANCE CHARTS (UPDATED) ==========
    with tab2:
        st.header("Performance Analysis")
        
        # Equity Curve with Drawdown
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=("Equity Curve (Time-Based)", "Drawdown"),
            vertical_spacing=0.1,
            shared_xaxes=True
        )
        
        # Equity curve (Now using Date Index)
        fig.add_trace(
            go.Scatter(
                x=results['equity_curve'].index,
                y=results['equity_curve'].values,
                mode='lines',
                name='Equity',
                line=dict(color='#00cc00', width=2),
                fill='tozeroy',
                fillcolor='rgba(0, 204, 0, 0.1)'
            ),
            row=1, col=1
        )
        
        # Drawdown
        fig.add_trace(
            go.Scatter(
                x=results['drawdown_curve'].index,
                y=results['drawdown_curve'].values,
                mode='lines',
                name='Drawdown',
                line=dict(color='#ff3333', width=2),
                fill='tozeroy',
                fillcolor='rgba(255, 51, 51, 0.1)'
            ),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Cumulative P/L ($)", row=1, col=1)
        fig.update_yaxes(title_text="Drawdown ($)", row=2, col=1)
        
        fig.update_layout(
            height=700,
            showlegend=True,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Win/Loss Distribution & Grades
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Win/Loss Distribution")
            
            # Histogram of P/L
            fig_hist = go.Figure()
            
            if 'processed_df' in results and not results['processed_df'].empty:
                wins_data = results['processed_df'][results['processed_df']['FifoPnlRealized'] > 0]['FifoPnlRealized']
                losses_data = results['processed_df'][results['processed_df']['FifoPnlRealized'] < 0]['FifoPnlRealized']
                
                fig_hist.add_trace(go.Histogram(
                    x=wins_data,
                    name='Wins',
                    marker_color='#00cc00',
                    opacity=0.7,
                    nbinsx=30
                ))
                
                fig_hist.add_trace(go.Histogram(
                    x=losses_data,
                    name='Losses',
                    marker_color='#ff3333',
                    opacity=0.7,
                    nbinsx=30
                ))
            
            fig_hist.update_layout(
                barmode='overlay',
                xaxis_title='P/L ($)',
                yaxis_title='Frequency',
                height=400
            )
            
            st.plotly_chart(fig_hist, width='stretch')
        
        with col2:
            st.subheader("Trade Grades")
            
            grade_order = ['A+', 'A', 'B', 'C', 'D', 'F']
            grade_colors = {
                'A+': '#00cc00', 'A': '#66ff66', 'B': '#ffcc00',
                'C': '#ff9900', 'D': '#ff6600', 'F': '#ff3333'
            }
            
            grades = []
            counts = []
            colors = []
            
            for grade in grade_order:
                if grade in results['grade_distribution']:
                    grades.append(grade)
                    counts.append(results['grade_distribution'][grade])
                    colors.append(grade_colors.get(grade, '#cccccc'))
            
            fig_grades = go.Figure(data=[
                go.Bar(
                    x=grades,
                    y=counts,
                    marker_color=colors,
                    text=counts,
                    textposition='auto'
                )
            ])
            
            fig_grades.update_layout(
                xaxis_title='Grade',
                yaxis_title='Number of Trades',
                height=400
            )
            
            st.plotly_chart(fig_grades, width='stretch')
        
        # Fear Index
        st.subheader("🧠 Fear Index")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric(
                "Fear Index",
                f"{results['fear_index']:.1f}%",
                help="Percentage of wins that were cut early (below 30% of average win)"
            )
            
            if results['fear_index'] > 50:
                st.error("You're exiting winners too early!")
            elif results['fear_index'] > 30:
                st.warning("Moderate fear - could let winners run more")
            else:
                st.success("Good discipline - letting winners run!")
        
        with col2:
            # Gauge chart for fear index
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=results['fear_index'],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Fear Index"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 30], 'color': "lightgreen"},
                        {'range': [30, 50], 'color': "yellow"},
                        {'range': [50, 100], 'color': "lightcoral"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, width='stretch')
    
    # ========== TAB 3: SYMBOL ANALYSIS ==========
    with tab3:
        st.header("Per-Symbol Performance")
        
        st.info("💡 **Symbols highlighted in yellow have open positions** (total quantity > 0)")
        
        # Format the dataframe
        symbol_df = results['symbol_stats'].copy()
        
        # Color code the net P/L
        def color_pnl(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'gray'
            return f'color: {color}'
        
        if not symbol_df.empty:
            styled_df = symbol_df.style.map(color_pnl, subset=['NetPnL'])
        # Highlight symbols with open positions
        def highlight_open(row):
            if row.get('HasOpenPosition', False):
                return ['background-color: #fff3cd'] * len(row)
            return [''] * len(row)
        
        styled_df = styled_df.apply(highlight_open, axis=1)
        
        st.dataframe(styled_df, width='stretch', height=400)
        
        # Top performers chart
        st.subheader("Top 10 Symbols by Net P/L")
        top_10 = symbol_df.nlargest(10, 'NetPnL')
        
        fig_symbols = go.Figure(data=[
            go.Bar(
                x=top_10['NetPnL'],
                y=top_10['Symbol'],
                orientation='h',
                marker_color=['green' if x > 0 else 'red' for x in top_10['NetPnL']],
                text=[f"${x:,.2f}" for x in top_10['NetPnL']],
                textposition='auto'
            )
        ])
        
        fig_symbols.update_layout(
            xaxis_title='Net P/L ($)',
            yaxis_title='Symbol',
            height=500,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig_symbols, width='stretch')
    
    # ========== TAB 4: TIME ANALYSIS ==========
    with tab4:
        st.header("Time-Based Analysis")
        
        # Day of week performance
        st.subheader("📅 Performance by Day of Week")
        
        if not results['dow_performance'].empty:
            dow_df = results['dow_performance'].reset_index()
            dow_df.columns = ['Day', 'Total P/L', 'Avg P/L', 'Trades']
            
            fig_dow = go.Figure(data=[
                go.Bar(
                    x=dow_df['Day'],
                    y=dow_df['Total P/L'],
                    marker_color=['green' if x > 0 else 'red' for x in dow_df['Total P/L']],
                    text=[f"${x:,.0f}" for x in dow_df['Total P/L']],
                    textposition='auto'
                )
            ])
            
            fig_dow.update_layout(
                xaxis_title='Day of Week',
                yaxis_title='Total P/L ($)',
                height=400
            )
            st.plotly_chart(fig_dow, width='stretch')
            st.dataframe(dow_df, width='stretch')
        
        # Monthly performance
        st.subheader("📊 Monthly Performance")
        
        if not results['monthly_performance'].empty:
            monthly_df = results['monthly_performance'].reset_index()
            monthly_df.columns = ['Month', 'Total P/L', 'Trades']
            
            fig_monthly = go.Figure(data=[
                go.Bar(
                    x=monthly_df['Month'],
                    y=monthly_df['Total P/L'],
                    marker_color=['green' if x > 0 else 'red' for x in monthly_df['Total P/L']],
                    text=[f"${x:,.0f}" for x in monthly_df['Total P/L']],
                    textposition='auto'
                )
            ])
            
            fig_monthly.update_layout(
                xaxis_title='Month',
                yaxis_title='Total P/L ($)',
                height=400
            )
            st.plotly_chart(fig_monthly, width='stretch')
            st.dataframe(monthly_df, width='stretch')
    
    # ========== TAB 5: BEST/WORST TRADES ==========
    with tab5:
        st.header("🏆 Top Winners & Losers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌟 Top 5 Winners")
            winners_df = results['top_winners'].copy()
            if not winners_df.empty:
                winners_df['TradeDate'] = pd.to_datetime(winners_df['TradeDate']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    winners_df.style.format({
                        'FifoPnlRealized': '${:,.2f}',
                        'IBCommission': '${:,.2f}'
                    }),
                    width='stretch'
                )
        
        with col2:
            st.subheader("💔 Top 5 Losers")
            losers_df = results['top_losers'].copy()
            if not losers_df.empty:
                losers_df['TradeDate'] = pd.to_datetime(losers_df['TradeDate']).dt.strftime('%Y-%m-%d')
                st.dataframe(
                    losers_df.style.format({
                        'FifoPnlRealized': '${:,.2f}',
                        'IBCommission': '${:,.2f}'
                    }),
                    width='stretch'
                )
    
    # ========== TAB 6: HOLDINGS DASHBOARD ==========
    with tab6:
        st.header("💼 Current Holdings Dashboard")
        
        # Analyze current holdings
        with st.spinner("Fetching current prices and sector data..."):
            holdings_data = analyze_current_holdings(df_filtered)
        
        if holdings_data['holdings'].empty:
            st.info("📭 No open positions found. All positions are closed.")
        else:
            # Portfolio Summary
            st.subheader("📊 Portfolio Summary")
            
            # Calculate totals
            total_cost_basis = holdings_data['holdings']['Cost Basis'].sum()
            total_market_value = holdings_data['total_market_value']
            total_unrealized_pnl = total_market_value - total_cost_basis
            total_unrealized_pnl_pct = (total_unrealized_pnl / total_cost_basis * 100) if total_cost_basis > 0 else 0
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Cost Basis",
                    f"${total_cost_basis:,.2f}",
                    help="Total amount invested in current holdings"
                )
            
            with col2:
                st.metric(
                    "Total Market Value",
                    f"${total_market_value:,.2f}",
                    help="Current value of all holdings"
                )
            
            with col3:
                pnl_delta = "+" if total_unrealized_pnl >= 0 else ""
                st.metric(
                    "Unrealized P/L",
                    f"${total_unrealized_pnl:,.2f}",
                    delta=f"{pnl_delta}{total_unrealized_pnl_pct:.2f}%",
                    help="Profit/Loss on open positions"
                )
            
            with col4:
                st.metric(
                    "Holdings / Sectors",
                    f"{len(holdings_data['holdings'])} / {len(holdings_data['sector_allocation'])}",
                    help="Number of stocks and sectors"
                )
            
            st.divider()
            
            # Sector Allocation
            #col1, col2 = st.columns([2, 1])
            
            #with col1:
            st.subheader("🎯 Sector Allocation")
            
            # Pie chart
            sector_df = holdings_data['sector_allocation']
            
            fig_pie = go.Figure(data=[go.Pie(
                labels=sector_df['Sector'],
                values=sector_df['Market Value'],
                hole=0.4,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>' +
                                'Value: $%{value:,.2f}<br>' +
                                'Percentage: %{percent}<br>' +
                                '<extra></extra>'
            )])
            
            fig_pie.update_layout(
                showlegend=True,
                height=500,
                title="Portfolio by Sector",
                margin=dict(l=20, r=20, t=40, b=100)  # Add this line! b=bottom padding
            )
            
            st.plotly_chart(fig_pie, width='stretch')
        
            st.divider()

            #with col2:
            st.subheader("📋 Sector Breakdown")
                
            # Format sector allocation table
            sector_display = sector_df.copy()
            sector_display['Market Value'] = sector_display['Market Value'].apply(lambda x: f"${x:,.2f}")
            sector_display['% of Portfolio'] = sector_display['% of Portfolio'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                sector_display,
                width='stretch',
                hide_index=True
            )
            
            st.divider()
            
            # Holdings Table
            st.subheader("📈 Individual Holdings")
            
            holdings_display = holdings_data['holdings'].copy()
            
            # Format columns for display
            holdings_display['Quantity'] = holdings_display['Quantity'].apply(lambda x: f"{x:.0f}")
            holdings_display['Avg Cost'] = holdings_display['Avg Cost'].apply(lambda x: f"${x:.2f}")
            holdings_display['Current Price'] = holdings_display['Current Price'].apply(lambda x: f"${x:.2f}")
            holdings_display['Cost Basis'] = holdings_display['Cost Basis'].apply(lambda x: f"${x:,.2f}")
            holdings_display['Market Value'] = holdings_display['Market Value'].apply(lambda x: f"${x:,.2f}")
            holdings_display['Unrealized P/L'] = holdings_display['Unrealized P/L'].apply(lambda x: f"${x:,.2f}")
            holdings_display['Unrealized P/L %'] = holdings_display['Unrealized P/L %'].apply(lambda x: f"{x:+.2f}%")
            holdings_display['% of Portfolio'] = holdings_display['% of Portfolio'].apply(lambda x: f"{x:.1f}%")
            holdings_display['Last Trade Date'] = pd.to_datetime(holdings_display['Last Trade Date']).dt.strftime('%Y-%m-%d')
            
            # Reorder columns for better readability
            column_order = ['Symbol', 'Quantity', 'Avg Cost', 'Current Price', 'Cost Basis', 
                           'Market Value', 'Unrealized P/L', 'Unrealized P/L %', '% of Portfolio', 
                           'Sector', 'Industry', 'Last Trade Date']
            holdings_display = holdings_display[column_order]
            
            # Color code the unrealized P/L column
            def color_pnl(val):
                if isinstance(val, str):
                    if val.startswith('+') or (val.startswith('$') and not val.startswith('$-')):
                        return 'color: green'
                    elif val.startswith('-') or val.startswith('$-'):
                        return 'color: red'
                return ''
            
            # Apply styling
            styled_holdings = holdings_display.style.map(
                color_pnl, 
                subset=['Unrealized P/L', 'Unrealized P/L %']
            )
            
            # Display table
            st.dataframe(
                styled_holdings,
                width='stretch',
                hide_index=True,
                height=400
            )
            
            st.divider()
            
            # Top Holdings
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🏆 Top 5 Holdings by Value")
                
                top_5 = holdings_data['holdings'].nlargest(5, 'Market Value')
                
                fig_top = go.Figure(data=[
                    go.Bar(
                        x=top_5['Market Value'],
                        y=top_5['Symbol'],
                        orientation='h',
                        marker_color='#00cc00',
                        text=[f"${x:,.0f}" for x in top_5['Market Value']],
                        textposition='auto'
                    )
                ])
                
                fig_top.update_layout(
                    xaxis_title='Market Value ($)',
                    yaxis_title='Symbol',
                    height=300,
                    yaxis={'categoryorder': 'total ascending'}
                )
                
                st.plotly_chart(fig_top, width='stretch')
            
            with col2:
                st.subheader("📊 Concentration Risk")
                
                # Calculate concentration
                top_5_pct = top_5['% of Portfolio'].sum()
                
                st.metric("Top 5 Holdings", f"{top_5_pct:.1f}%", 
                         help="Percentage of portfolio in top 5 holdings")
                
                if top_5_pct > 70:
                    st.warning("⚠️ High concentration risk (>70% in top 5)")
                elif top_5_pct > 50:
                    st.info("🟡 Moderate concentration (50-70% in top 5)")
                else:
                    st.success("✅ Well diversified (<50% in top 5)")
                
                # Sector concentration
                max_sector_pct = holdings_data['sector_allocation']['% of Portfolio'].max()
                max_sector = holdings_data['sector_allocation'].loc[
                    holdings_data['sector_allocation']['% of Portfolio'].idxmax(), 'Sector'
                ]
                
                st.metric(
                    f"Largest Sector ({max_sector})",
                    f"{max_sector_pct:.1f}%"
                )
                
                if max_sector_pct > 50:
                    st.warning(f"⚠️ Heavy concentration in {max_sector}")
                elif max_sector_pct > 30:
                    st.info(f"🟡 Moderate exposure to {max_sector}")
                else:
                    st.success("✅ Good sector diversification")

    # ========== TAB 7: RAW DATA ==========
    with tab7:
        st.header("📄 Raw Trade Data")
        
        if not results['processed_df'].empty:
            display_df = results['processed_df'][
                ['TradeDate', 'Symbol', 'Buy/Sell', 'Quantity', 
                 'FifoPnlRealized', 'IBCommission', 'Grade']
            ].copy()
            
            display_df['TradeDate'] = pd.to_datetime(display_df['TradeDate']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            st.dataframe(
                display_df.style.format({
                    'FifoPnlRealized': '${:,.2f}',
                    'IBCommission': '${:,.2f}',
                    'Quantity': '{:,.0f}'
                }),
                width='stretch',
                height=600
            )
            
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Processed Data",
                data=csv,
                file_name="processed_trades.csv",
                mime="text/csv"
            )

else:
    # Landing page
    st.info("👆 Upload your IBKR trade CSV file to get started!")
    st.markdown("""
    ### Features (Pro Version):
    - **Comprehensive Metrics**: Win rate, profit factor, expectancy, R/R ratio.
    - **Visual Analytics**: Interactive time-based equity curve, drawdown.
    - **Symbol Breakdown**: Net P/L analysis per symbol (including all commissions).
    - **Time Analysis**: Performance by Day of Week and Month.
    - **Behavioral Insights**: Fear index, trade grading, and smart alerts.
    """)