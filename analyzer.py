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