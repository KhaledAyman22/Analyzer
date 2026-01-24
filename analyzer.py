import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_trades(df):
    """
    Enhanced trade analyzer with comprehensive metrics and insights.
    Revised to include ALL commissions and Time-Based Equity Curve.
    """
    # ==============================================================================
    # 1. CLEANUP & PREPARATION
    # ==============================================================================
    df = df.copy()
    df.columns = df.columns.str.strip()
    
    # Ensure standard columns exist and are numeric
    cols_to_numeric = ["FifoPnlRealized", "IBCommission", "Quantity"]
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            
    df["TradeDate"] = pd.to_datetime(df["TradeDate"])
    
    # Calculate Per-Row Net (for grading individual actions)
    # Note: This is partial net (gross + exit fee usually)
    # FifoPnlRealized IS ALREADY NET (after commissions)
    
    # Sort by date
    df = df.sort_values("TradeDate").reset_index(drop=True)

    # ==============================================================================
    # 2. GLOBAL FINANCIALS (The Fix for "Missing Commissions")
    # ==============================================================================
    # We sum the ENTIRE dataframe to capture every cent of commission paid, 
    # even on opening trades or trades not yet closed.
    
    # FifoPnlRealized is ALREADY the net P/L (after commissions)
    total_pnl_net = df["FifoPnlRealized"].sum()
    total_fees = df["IBCommission"].sum()  # For informational purposes only
    
    # Commission Analysis
    commission_pct = (abs(total_fees) / abs(total_pnl_net) * 100) if total_pnl_net != 0 else 0
    total_trades_count_all_rows = len(df)
    avg_commission_per_trade = total_fees / total_trades_count_all_rows if total_trades_count_all_rows > 0 else 0

    # ==============================================================================
    # 3. EQUITY CURVE (The Fix for "Weird Graphs")
    # ==============================================================================
    # Aggregate by Date first. This creates a proper time-series.
    # Aggregate by date - FifoPnlRealized is already net
    daily_stats = df.groupby(df["TradeDate"].dt.date)["FifoPnlRealized"].sum().to_frame()
    daily_stats.rename(columns={"FifoPnlRealized": "DailyNet"}, inplace=True)
    
    # Create the curve
    equity_curve = daily_stats["DailyNet"].cumsum()
    
    # Calculate drawdown based on the time series
    running_max = equity_curve.cummax()
    drawdown = equity_curve - running_max
    max_drawdown = drawdown.min()
    
    # Max DD % (Approximated based on running max equity, assuming starting at 0)
    # Adding a small epsilon or handling 0 to avoid div by zero
    max_drawdown_pct = 0
    if running_max.max() > 0:
        max_drawdown_pct = (max_drawdown / running_max.max() * 100)

    # Drawdown duration (Time based now)
    max_dd_duration = 0
    if len(drawdown) > 0:
        is_dd = drawdown < 0
        # Calculate streaks of days in drawdown
        dd_days = is_dd.astype(int).groupby(is_dd.ne(is_dd.shift()).cumsum()).cumsum()
        max_dd_duration = dd_days.where(is_dd).max()
        if pd.isna(max_dd_duration): max_dd_duration = 0

    # ==============================================================================
    # 4. CLOSED TRADE STATISTICS (For Win Rate, Avg Win, etc.)
    # ==============================================================================
    # We still need to isolate "Closed Trades" to calculate Win Rate.
    # We cannot calculate a "Win Rate" on an opening buy order.
    closed_trades = df[df["FifoPnlRealized"] != 0].copy()
    
    total_trades = len(closed_trades)
    
    if total_trades > 0:
        wins = closed_trades[closed_trades["FifoPnlRealized"] > 0]
        losses = closed_trades[closed_trades["FifoPnlRealized"] < 0]
        breakeven = closed_trades[closed_trades["FifoPnlRealized"] == 0]
        
        num_wins = len(wins)
        num_losses = len(losses)
        num_breakeven = len(breakeven)
        
        win_rate = (num_wins / total_trades * 100)
        
        avg_win = wins["FifoPnlRealized"].mean() if len(wins) > 0 else 0
        avg_loss = losses["FifoPnlRealized"].mean() if len(losses) > 0 else 0
        
        largest_win = wins["FifoPnlRealized"].max() if len(wins) > 0 else 0
        largest_loss = losses["FifoPnlRealized"].min() if len(losses) > 0 else 0
        
        # Profit Factor
        gross_profit = wins["FifoPnlRealized"].sum() if len(wins) > 0 else 0
        gross_loss = abs(losses["FifoPnlRealized"].sum()) if len(losses) > 0 else 0
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else np.inf
        
        # Risk/Reward
        avg_rr_ratio = (abs(avg_win) / abs(avg_loss)) if avg_loss != 0 else 0
        
        # Expectancy
        expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
        
    else:
        # Defaults if no closed trades
        wins, losses = pd.DataFrame(), pd.DataFrame()
        num_wins, num_losses, num_breakeven = 0, 0, 0
        win_rate, avg_win, avg_loss = 0, 0, 0
        largest_win, largest_loss = 0, 0
        profit_factor, avg_rr_ratio, expectancy = 0, 0, 0

    # ==============================================================================
    # 5. STREAKS
    # ==============================================================================
    max_win_streak = 0
    max_loss_streak = 0
    
    if len(closed_trades) > 0:
        closed_trades['IsWin'] = closed_trades['FifoPnlRealized'] > 0
        # Calculate streaks using vectorization
        streak_groups = closed_trades['IsWin'].ne(closed_trades['IsWin'].shift()).cumsum()
        streaks = closed_trades.groupby(streak_groups)['IsWin'].agg(['first', 'size'])
        
        win_streaks = streaks[streaks['first'] == True]['size']
        loss_streaks = streaks[streaks['first'] == False]['size']
        
        max_win_streak = win_streaks.max() if not win_streaks.empty else 0
        max_loss_streak = loss_streaks.max() if not loss_streaks.empty else 0
    
    # ==============================================================================
    # 6. PER SYMBOL PERFORMANCE
    # ==============================================================================
    # We aggregate the FULL dataframe to ensure we catch commissions for symbols 
    # that might have been bought but not sold yet.
    symbol_stats = (
        df.groupby("Symbol")
        .agg(
            Trades=("FifoPnlRealized", lambda x: (x != 0).sum()), # Count realized events
            NetPnL=("FifoPnlRealized", "sum"),  # FifoPnlRealized is already net
            Fees=("IBCommission", "sum"),  # For information only
        )
    )
    
    # Calculate Wins/Losses (requires filtering for closed trades per symbol)
    if len(closed_trades) > 0:
        sym_wins = closed_trades[closed_trades['FifoPnlRealized'] > 0].groupby('Symbol').size()
        sym_losses = closed_trades[closed_trades['FifoPnlRealized'] < 0].groupby('Symbol').size()
        
        symbol_stats['Wins'] = symbol_stats.index.map(sym_wins).fillna(0)
        symbol_stats['Losses'] = symbol_stats.index.map(sym_losses).fillna(0)
    else:
        symbol_stats['Wins'] = 0
        symbol_stats['Losses'] = 0
        
    # Calculate Win Rate
    symbol_stats['WinRate'] = (symbol_stats['Wins'] / symbol_stats['Trades'] * 100).fillna(0)
    
    # Add Best/Worst trade per symbol
    if len(closed_trades) > 0:
        symbol_stats['BestTrade'] = closed_trades.groupby('Symbol')['FifoPnlRealized'].max()
        symbol_stats['WorstTrade'] = closed_trades.groupby('Symbol')['FifoPnlRealized'].min()
    else:
        symbol_stats['BestTrade'] = 0
        symbol_stats['WorstTrade'] = 0

    # Mark symbols with open positions (Quantity sum > 0 means position is still open)
    position_check = df.groupby('Symbol')['Quantity'].sum()
    symbol_stats['OpenPosition'] = symbol_stats.index.map(position_check).fillna(0)
    symbol_stats['HasOpenPosition'] = symbol_stats['OpenPosition'] > 0
    
    # Calculate average P/L per trade
    symbol_stats['AvgPnL'] = (symbol_stats['NetPnL'] / symbol_stats['Trades']).fillna(0)
    
    symbol_stats = symbol_stats.sort_values("NetPnL", ascending=False).reset_index()
    
    # ==============================================================================
    # 7. TIME-BASED ANALYSIS (Restored)
    # ==============================================================================
    closed_trades['DayOfWeek'] = closed_trades['TradeDate'].dt.day_name()
    closed_trades['Month'] = closed_trades['TradeDate'].dt.to_period('M')
    
    # Day of week performance
    dow_performance = (
        closed_trades.groupby('DayOfWeek')['FifoPnlRealized']
        .agg(['sum', 'mean', 'count'])
        .round(2)
    )
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_performance = dow_performance.reindex([d for d in day_order if d in dow_performance.index])
    
    # Monthly performance
    monthly_performance = (
        closed_trades.groupby('Month')['FifoPnlRealized']
        .agg(['sum', 'count'])
        .round(2)
    )
    monthly_performance.index = monthly_performance.index.astype(str)
    
    # ==============================================================================
    # 8. FEAR INDEX & GRADING (Restored)
    # ==============================================================================
    if len(wins) > 0 and avg_win > 0:
        small_win_threshold = avg_win * 0.3
        small_wins = wins[wins["FifoPnlRealized"] < small_win_threshold]
        fear_index = (len(small_wins) / len(wins)) * 100
    else:
        fear_index = 0
    
    # Grading Logic
    def grade_trade(pnl, fee):
        net = pnl + fee 
        fee_cost = abs(fee) if fee != 0 else 0.01 # avoid div by zero
        
        if net > 5 * fee_cost: return "A+"
        elif net > 3 * fee_cost: return "A"
        elif net > fee_cost: return "B"
        elif net > 0: return "C"
        elif net > -fee_cost: return "D"
        else: return "F"
    
    closed_trades["Grade"] = closed_trades.apply(
        lambda x: grade_trade(x["FifoPnlRealized"], x["IBCommission"]), axis=1
    )
    grade_dist = closed_trades["Grade"].value_counts().to_dict()
    
    # ==============================================================================
    # 9. INSIGHTS GENERATION (Restored)
    # ==============================================================================
    insights = []
    
    if win_rate < 40: insights.append("⚠️ Low win rate (<40%). Consider improving trade selection.")
    elif win_rate > 70: insights.append("✅ High win rate (>70%). Good trade selection!")
    
    if avg_win > 0 and avg_loss < 0:
        if avg_rr_ratio < 1.5: insights.append("⚠️ Risk/Reward ratio below 1.5:1. Losses are too large relative to wins.")
        elif avg_rr_ratio > 2.5: insights.append("✅ Excellent Risk/Reward ratio (>2.5:1)!")
    
    if profit_factor < 1: insights.append("🚨 Profit factor <1. Overall unprofitable.")
    elif profit_factor > 2: insights.append("✅ Strong profit factor (>2)!")
    
    if fear_index > 50: insights.append("🧠 High Fear Index (>50%). You are cutting winners too early.")
    
    if commission_pct > 30: insights.append("💸 Commissions eating >30% of gross profits. Reduce frequency or increase size.")
    
    if max_loss_streak >= 5: insights.append(f"⚠️ Long losing streak ({max_loss_streak} trades).")
    
    if expectancy > 0: insights.append(f"✅ Positive expectancy (${expectancy:.2f} per trade).")
    else: insights.append(f"🚨 Negative expectancy (${expectancy:.2f} per trade).")
    
    if len(dow_performance) > 0:
        best_day = dow_performance['sum'].idxmax()
        insights.append(f"📅 Best day: {best_day}")

    # ==============================================================================
    # 10. FINAL RETURN
    # ==============================================================================
    top_winners = closed_trades.nlargest(5, 'FifoPnlRealized')[['TradeDate', 'Symbol', 'FifoPnlRealized', 'IBCommission']]
    top_losers = closed_trades.nsmallest(5, 'FifoPnlRealized')[['TradeDate', 'Symbol', 'FifoPnlRealized', 'IBCommission']]

    return {
        "total_trades": total_trades,
        "num_wins": num_wins,
        "num_losses": num_losses,
        "num_breakeven": num_breakeven,
        "win_rate": win_rate,
        
        "total_fees": total_fees,
        "total_pnl_net": total_pnl_net,
        
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "largest_win": largest_win,
        "largest_loss": largest_loss,
        
        "profit_factor": profit_factor,
        "avg_rr_ratio": avg_rr_ratio,
        "expectancy": expectancy,
        
        "max_drawdown": max_drawdown,
        "max_drawdown_pct": max_drawdown_pct,
        "max_dd_duration": max_dd_duration,
        
        "max_win_streak": max_win_streak,
        "max_loss_streak": max_loss_streak,
        
        "commission_pct": commission_pct,
        "avg_commission_per_trade": avg_commission_per_trade,
        
        # New Time Series Data
        "equity_curve": equity_curve, 
        "drawdown_curve": drawdown,
        
        "symbol_stats": symbol_stats,
        "dow_performance": dow_performance,
        "monthly_performance": monthly_performance,
        
        "fear_index": fear_index,
        "grade_distribution": grade_dist,
        
        "top_winners": top_winners,
        "top_losers": top_losers,
        
        "insights": insights,
        "processed_df": closed_trades,
    }


def analyze_current_holdings(df):
    """
    Analyze current holdings (open positions) with sector information.
    Returns holdings with sector breakdown and allocation percentages.
    
    NOTE: Queries unique tickers only (grouped by Symbol first).
    Uses batch fetching and threading for speed.
    """
    import yfinance as yf
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    # Calculate average cost basis for each symbol using FIFO
    def calculate_avg_cost(symbol_df):
        # Sort by date to process in order
        symbol_df = symbol_df.sort_values('TradeDate').reset_index(drop=True)
        
        # Track lots (FIFO queue)
        lots = []  # Each lot: {'quantity': qty, 'price': price}
        
        for _, row in symbol_df.iterrows():
            qty = row['Quantity']
            price = row['TradePrice']
            
            if qty > 0:  # BUY - add new lot
                # Include commission in cost basis
                commission_per_share = abs(row['IBCommission']) / qty
                price_with_commission = price + commission_per_share
                lots.append({'quantity': qty, 'price': price_with_commission})
            
            else:  # SELL - remove from oldest lots (FIFO)
                sell_qty = abs(qty)
                remaining_to_sell = sell_qty
                
                while remaining_to_sell > 0 and len(lots) > 0:
                    if lots[0]['quantity'] <= remaining_to_sell:
                        # Sell entire oldest lot
                        remaining_to_sell -= lots[0]['quantity']
                        lots.pop(0)
                    else:
                        # Partially sell oldest lot
                        lots[0]['quantity'] -= remaining_to_sell
                        remaining_to_sell = 0
        
        # Calculate weighted average of remaining lots
        if len(lots) == 0:
            return 0
        
        total_cost = sum(lot['quantity'] * lot['price'] for lot in lots)
        total_shares = sum(lot['quantity'] for lot in lots)
        
        return total_cost / total_shares if total_shares > 0 else 0
    
    # Calculate position for each symbol (this gives us UNIQUE symbols only)
    position_data = []
    for symbol in df['Symbol'].unique():
        symbol_df = df[df['Symbol'] == symbol]
        
        position_data.append({
            'Symbol': symbol,
            'Quantity': symbol_df['Quantity'].sum(),
            'AvgCostBasis': calculate_avg_cost(symbol_df),
            'LastTradePrice': symbol_df['TradePrice'].iloc[-1],
            'TradeDate': symbol_df['TradeDate'].iloc[-1]
        })
    
    position_summary = pd.DataFrame(position_data)
    
    # Filter for open positions only (Quantity > 0)
    open_positions = position_summary[position_summary['Quantity'] > 0].copy()
    
    if len(open_positions) == 0:
        return {
            'holdings': pd.DataFrame(),
            'sector_allocation': pd.DataFrame(),
            'total_market_value': 0,
            'sector_summary': {}
        }
    
    # Get unique symbols to query (explicit confirmation)
    unique_symbols = open_positions['Symbol'].unique().tolist()
    print(f"Fetching data for {len(unique_symbols)} unique symbols: {', '.join(unique_symbols)}")
    
    # Fetch ticker data in parallel (MUCH FASTER!)
    def fetch_ticker_data(symbol_data):
        symbol = symbol_data['symbol']
        quantity = symbol_data['quantity']
        avg_cost = symbol_data['avg_cost']
        last_price = symbol_data['last_price']
        last_date = symbol_data['last_date']
        
        try:
            ticker = yf.Ticker(symbol)
            
            # Get current price (fast)
            try:
                current_price = ticker.fast_info['lastPrice']
            except:
                current_price = last_price
            
            # Get sector/industry (slower, but necessary)
            try:
                info = ticker.info
                sector = info.get('sector', info.get('category', 'Unknown'))
                industry = info.get('industry', 'Unknown')
            except:
                sector = 'Unknown'
                industry = 'Unknown'
            
            # Calculate P/L
            cost_basis = quantity * avg_cost
            market_value = quantity * current_price
            unrealized_pnl = market_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            return {
                'Symbol': symbol,
                'Quantity': quantity,
                'Avg Cost': avg_cost,
                'Current Price': current_price,
                'Cost Basis': cost_basis,
                'Market Value': market_value,
                'Unrealized P/L': unrealized_pnl,
                'Unrealized P/L %': unrealized_pnl_pct,
                'Sector': sector,
                'Industry': industry,
                'Last Trade Date': last_date
            }
        except Exception as e:
            # Fallback to last known price
            cost_basis = quantity * avg_cost
            market_value = quantity * last_price
            unrealized_pnl = market_value - cost_basis
            unrealized_pnl_pct = (unrealized_pnl / cost_basis * 100) if cost_basis > 0 else 0
            
            return {
                'Symbol': symbol,
                'Quantity': quantity,
                'Avg Cost': avg_cost,
                'Current Price': last_price,
                'Cost Basis': cost_basis,
                'Market Value': market_value,
                'Unrealized P/L': unrealized_pnl,
                'Unrealized P/L %': unrealized_pnl_pct,
                'Sector': 'Unknown',
                'Industry': 'Unknown',
                'Last Trade Date': last_date
            }
    
    # Prepare data for parallel fetching
    symbols_to_fetch = [
        {
            'symbol': row['Symbol'],
            'quantity': row['Quantity'],
            'avg_cost': row['AvgCostBasis'],
            'last_price': row['LastTradePrice'],
            'last_date': row['TradeDate']
        }
        for _, row in open_positions.iterrows()
    ]
    
    # Fetch all tickers in parallel
    holdings_data = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_ticker_data, data) for data in symbols_to_fetch]
        for future in as_completed(futures):
            holdings_data.append(future.result())
    
    # Create holdings dataframe
    holdings_df = pd.DataFrame(holdings_data)
    
    if len(holdings_df) == 0:
        return {
            'holdings': pd.DataFrame(),
            'sector_allocation': pd.DataFrame(),
            'total_market_value': 0,
            'sector_summary': {}
        }
    
    # Calculate total portfolio value
    total_market_value = holdings_df['Market Value'].sum()
    
    # Add allocation percentage
    holdings_df['% of Portfolio'] = (holdings_df['Market Value'] / total_market_value * 100).round(2)
    
    # Sort by market value
    holdings_df = holdings_df.sort_values('Market Value', ascending=False)
    
    # Calculate sector allocation
    sector_allocation = holdings_df.groupby('Sector').agg({
        'Market Value': 'sum',
        'Symbol': 'count'
    }).reset_index()
    sector_allocation.columns = ['Sector', 'Market Value', 'Number of Stocks']
    sector_allocation['% of Portfolio'] = (sector_allocation['Market Value'] / total_market_value * 100).round(2)
    sector_allocation = sector_allocation.sort_values('Market Value', ascending=False)
    
    # Create sector summary dictionary
    sector_summary = {}
    for _, row in sector_allocation.iterrows():
        sector_summary[row['Sector']] = {
            'value': row['Market Value'],
            'percentage': row['% of Portfolio'],
            'count': int(row['Number of Stocks'])
        }
    
    return {
        'holdings': holdings_df,
        'sector_allocation': sector_allocation,
        'total_market_value': total_market_value,
        'sector_summary': sector_summary
    }


def filter_trades_by_date(df, start_date=None, end_date=None):
    df['TradeDate'] = pd.to_datetime(df['TradeDate'])
    if start_date:
        df = df[df['TradeDate'] >= pd.to_datetime(start_date)]
    if end_date:
        df = df[df['TradeDate'] <= pd.to_datetime(end_date)]
    return df

def filter_trades_by_symbol(df, symbols):
    if symbols:
        return df[df['Symbol'].isin(symbols)]
    return df