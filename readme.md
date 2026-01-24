# 📊 Trading Performance Analyzer Pro

A comprehensive trading analytics tool for analyzing IBKR (Interactive Brokers) trade data. Get deep insights into your trading performance with advanced metrics, visualizations, behavioral analysis, and **real-time portfolio tracking**.

## 🚀 Quick Start

```bash
After you install Python, run runner.bat and you are ready to go. 
```

Upload your IBKR CSV containing (Symbol | TradeDate | Quantity | TradePrice | IBCommission | FifoPnlRealized | Buy/Sell) and start analyzing!

---

## 📋 Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Understanding Your Data](#understanding-your-data)
4. [Using the App](#using-the-app)
5. [Metrics Explained](#metrics-explained)
6. [What Good Numbers Look Like](#what-good-numbers-look-like)
7. [Pro Tips](#pro-tips)
8. [Troubleshooting](#troubleshooting)

---

## Features

### Core Metrics
- Win Rate, Profit Factor, Expectancy
- Risk/Reward Ratio
- Total P/L (already net of commissions)

### Risk Analysis
- Max Drawdown ($ and %)
- Drawdown Duration
- Time-based Equity Curve
- Win/Loss Streaks

### Behavioral Insights
- **Fear Index**: Measures early exit tendency (30% threshold)
- **Trade Grading**: A+ to F based on profit vs commission
- Overtrading alerts
- Commission impact analysis

### Symbol Analysis
- Performance per symbol
- **Open Position Tracking** (yellow highlighting)
- Win rate, best/worst trades per symbol

### Holdings Dashboard (NEW! 💼)
- **Real-time portfolio view** with live prices from Yahoo Finance
- **Accurate cost basis** using FIFO accounting (matches IBKR)
- **Sector allocation** with interactive pie chart
- **Unrealized P/L** tracking for open positions
- **Concentration risk warnings**
- Top 5 positions by value
- Individual holdings breakdown with:
  - Average cost per share (includes commissions)
  - Cost basis (total invested)
  - Current market value
  - Unrealized profit/loss ($ and %)
  - Portfolio allocation %
  - Sector/Industry classification

### Time Analysis
- Day of week performance
- Monthly tracking
- Top 5 winners/losers

### Interactive Features
- Date and symbol filters
- 7 organized tabs
- Export to CSV
- Professional charts with proper margins
- Parallel API fetching (fast loading)

---

## Installation

### Prerequisites
- Python 3.8 or higher

### Setup

1. **Download files:**
   - `analyzer.py`
   - `app.py`
   - `requirements.txt`

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run:**
   ```bash
   streamlit run app.py
   ```

4. **Open browser:**
   - Auto-opens at `http://localhost:8501`

---

## Understanding Your Data

### 🔑 CRITICAL: FifoPnlRealized IS Already NET!

**The most important thing to understand:**

`FifoPnlRealized` = Your ACTUAL profit/loss (already includes ALL commissions)

You do NOT need to add or subtract anything!

### Example
```
Buy 100 shares @ $10 = $1,000 + $1 commission
Sell 100 shares @ $12 = $1,200 - $1 commission

FifoPnlRealized shown on SELL row: $198
(Not $200! Already minus both $1 commissions)
```

### CSV Columns

**FifoPnlRealized**
- Your FINAL profit or loss
- Already has buy AND sell commissions deducted
- Sum this for total profit/loss
- This is what goes in your pocket

**IBCommission**  
- Fee for THIS transaction only
- Negative number (it's a cost)
- For information/tracking only
- **Do NOT subtract from FifoPnlRealized**

**Quantity**
- Positive = BUY
- Negative = SELL
- Sum by symbol to find open positions

---

## Using the App

### 7 Tabs Explained

#### 📊 Overview Tab

**Basic Stats:**
- Total Trades, Wins, Losses, Win Rate

**P/L Metrics:**
- **Total P/L**: Your actual profit (already net)
- **Total Fees**: Commissions paid (informational)
- **Fee Impact %**: What % went to fees

**Advanced Metrics:**
- **Profit Factor** (Total Wins ÷ Total Losses)
  - <1.0 = Losing
  - 1.5-2.0 = Good
  - />2.0 = Excellent
  
- **Expectancy** (Average $ per trade)
  - Positive = Profitable strategy
  - Higher = Better
  
- **R/R Ratio** (Avg Win ÷ Avg Loss)
  - <1.5 = Below average
  - 1.5-2.5 = Good
  - />2.5 = Excellent

**Risk Metrics:**
- Max Drawdown, Streaks

#### 📈 Performance Tab

- Clean equity curve (time-based)
- Drawdown chart
- Win/loss distribution
- Trade grade bar chart
- Fear Index gauge

#### 🎯 Symbol Analysis Tab

- Table of all symbols
- **Yellow = Open position** (Quantity sum > 0)
- NetPnL, win rate per symbol
- Top 10 chart

#### 📅 Time Analysis Tab

- Performance by day of week
- Monthly breakdown
- Identify patterns

#### 🏆 Best/Worst Trades Tab

- Top 5 winners
- Top 5 losers
- Learn from extremes

#### 💼 Holdings Dashboard Tab (NEW!)

**Real-Time Portfolio Tracking:**

**Portfolio Summary:**
- Total Cost Basis - Amount invested in open positions
- Total Market Value - Current value with live prices
- Total Unrealized P/L - Profit/loss on open positions ($ and %)
- Number of Holdings and Sectors

**Sector Allocation:**
- Interactive pie chart showing portfolio by sector
- Breakdown table with value and % per sector
- ETF handling (gets category/sector info)

**Individual Holdings Table:**
Shows for each open position:
- Symbol
- Quantity held
- **Average Cost** - FIFO cost basis (includes commissions!)
- Current Price (live from Yahoo Finance)
- Cost Basis - Total invested (Quantity × Avg Cost)
- Market Value - Current worth
- **Unrealized P/L ($)** - Profit/loss if you sold now
- **Unrealized P/L (%)** - Return on investment
- % of Portfolio
- Sector/Industry
- Last Trade Date

**Concentration Analysis:**
- Top 5 holdings by value (bar chart)
- Portfolio concentration warnings:
  - 🚨 Top 5 > 70%: High risk
  - 🟡 Top 5 50-70%: Moderate
  - ✅ Top 5 < 50%: Well diversified
- Sector concentration alerts:
  - 🚨 One sector > 50%: Heavy concentration
  - 🟡 One sector 30-50%: Moderate exposure
  - ✅ All sectors < 30%: Good diversification

**Key Features:**
- ✅ Matches IBKR cost basis (includes commissions)
- ✅ Fast parallel fetching (1-2 seconds for 10 stocks)
- ✅ Color-coded P/L (green for gains, red for losses)
- ✅ Identifies break-even prices
- ✅ Tax planning ready (shows unrealized gains)

#### 📄 Raw Data Tab

- All closed trades
- Export to CSV
- P/L, commission, grade

---

## Metrics Explained

### Fear Index (0-100%)

**Measures:** Do you exit winners too early?

**How it works:**
1. Calculate average winning trade
2. Set threshold at 30% of average win
3. Count wins below threshold
4. Fear Index = (small wins / total wins) × 100

**Example:**
- Avg win = $100
- Threshold = $30
- 6 of 10 wins under $30
- **Fear Index = 60%**

**Interpretation:**
- <20%: ✅ Excellent - let winners run
- 20-40%: 🟡 Moderate
- 40-60%: ⚠️ High - cutting too early
- />60%: 🚨 Severe psychological issue

---

### Trade Grades (A+ to F)

**Measures:** Trade quality vs commission cost

**Grading:**
- **A+**: Profit > 5× commission (Excellent)
- **A**: Profit > 3× commission (Very good)
- **B**: Profit > 1× commission (Good)
- **C**: Small profit (Barely profitable)
- **D**: Small loss (Minor)
- **F**: Large loss (Bad)

**Example ($1 commission):**
- Profit $6 = A+ (6× fee)
- Profit $4 = A (4× fee)
- Profit $2 = B (2× fee)
- Profit $0.50 = C (barely covered)
- Loss -$0.50 = D (small)
- Loss -$3 = F (3× fee lost)

**Good distribution:**
- A+/A: 20-30%
- B: 30-40%
- C: 20-30%
- D/F: <20%

---

### Profit Factor

**Formula:** Total Wins ÷ Total Losses

**Example:**
- Wins: $5,000
- Losses: $2,000
- **Profit Factor = 2.5**

**Interpretation:**
- <1.0: 🚨 Losing
- 1.0-1.5: ⚠️ Barely profitable
- 1.5-2.0: 🟡 Decent
- 2.0-3.0: ✅ Good
- />3.0: ✅ Excellent

---

### Expectancy

**Formula:** (Win Rate × Avg Win) + ((1 - Win Rate) × Avg Loss)

**Example:**
- Win Rate: 60%
- Avg Win: $100
- Avg Loss: -$50
- **Expectancy = $40/trade**

**Meaning:** Average profit per trade

**Interpretation:**
- Positive: ✅ Strategy works
- Negative: 🚨 Fix strategy
- Higher: Better

---

### Risk/Reward Ratio

**Formula:** Avg Win ÷ Avg Loss

**Example:**
- Avg Win: $150
- Avg Loss: -$100
- **R/R = 1.5:1**

**Interpretation:**
- <1.0: 🚨 Losses bigger than wins
- 1.0-1.5: ⚠️ Below average
- 1.5-2.5: ✅ Good
- />2.5: ✅ Excellent

**Key:** You can be profitable with 40% win rate if R/R > 2:1

---

### Average Cost Basis (Holdings Dashboard)

**What it is:** Weighted average price you paid for shares you **currently hold**.

**How it's calculated:**
Uses **FIFO (First-In-First-Out)** accounting:
1. Each BUY creates a "lot" at that price
2. Each SELL removes shares from oldest lots first
3. **Commissions are included** in the cost per share
4. Average = Total cost of remaining lots / Total remaining shares

**Example:**
```
Buy 100 @ $150 + $0.35 commission → Cost: $150.0035/share
Buy 50 @ $160 + $0.35 commission → Cost: $160.0070/share
Sell 50 (removes from first buy)
Remaining: 50@$150.0035 + 50@$160.0070
Avg Cost = (50×$150.0035 + 50×$160.0070) / 100 = $155.01
```

**Why it matters:**
- ✅ Matches IBKR calculations exactly
- ✅ Includes commissions (tax-accurate)
- ✅ Shows true break-even price
- ✅ Basis for unrealized P/L

---

### Unrealized P/L (Holdings Dashboard)

**What it is:** Profit or loss on positions you still hold (not yet sold).

**Formula:**
```
Unrealized P/L = Market Value - Cost Basis
Market Value = Quantity × Current Price
Cost Basis = Quantity × Average Cost

Unrealized P/L % = (Unrealized P/L / Cost Basis) × 100
```

**Example:**
```
Holding: 100 shares
Avg Cost: $150 (your entry)
Current Price: $160
Market Value: 100 × $160 = $16,000
Cost Basis: 100 × $150 = $15,000
Unrealized P/L: $16,000 - $15,000 = +$1,000
Unrealized P/L %: ($1,000 / $15,000) × 100 = +6.67%
```

**Why it matters:**
- Shows current position performance
- Helps decide when to take profits
- Indicates tax liability if you sell
- Combined with realized P/L = total trading return

---

### Max Drawdown

**Measures:** Worst losing streak impact

**Example:**
- Peak: $10,000
- Bottom: $8,000
- **Drawdown = -$2,000 (-20%)**

**Risk levels:**
- <10%: Low risk
- 10-20%: Moderate
- 20-30%: ⚠️ High risk
- />30%: 🚨 Very high risk

---

### Commission Impact

**Formula:** (Total Fees ÷ Total P/L) × 100

**Example:**
- Profit: $1,000
- Fees: $300
- **Impact = 30%**

**Interpretation:**
- <15%: ✅ Good
- 15-30%: 🟡 Acceptable
- 30-50%: ⚠️ High - reduce frequency
- />50%: 🚨 Overtrading

---

## What Good Numbers Look Like

| Metric | Beginner | Intermediate | Advanced |
|--------|----------|--------------|----------|
| Win Rate | 45-55% | 50-60% | 55-70% |
| Profit Factor | 1.2-1.5 | 1.5-2.0 | 2.0+ |
| R/R Ratio | 1.0-1.5 | 1.5-2.0 | 2.0+ |
| Expectancy | $5-20 | $20-50 | $50+ |
| Fear Index | 40-60% | 20-40% | <20% |
| Fee Impact | 30-50% | 15-30% | <15% |
| Max DD % | 20-40% | 10-20% | <10% |

---

## Trading Scenarios

### High Win Rate, Low R/R
```
Win Rate: 70%
R/R: 0.8:1
Profit Factor: 1.3
```
**Issue:** Losses bigger than wins. Fragile.  
**Fix:** Cut losses faster.

### Low Win Rate, High R/R  
```
Win Rate: 40%
R/R: 3:1
Profit Factor: 2.4
```
**Style:** Trend following. Many small losses, huge wins.  
**Works if:** You have discipline.

### Balanced (Ideal)
```
Win Rate: 55%
R/R: 1.8:1
Profit Factor: 2.2
Expectancy: $45
```
**Result:** Sustainable, professional.

---

## Pro Tips

1. **Focus on Expectancy**: If positive, strategy works

2. **Balance Win Rate & R/R**:
   - High win rate + low R/R = Cut losers faster
   - Low win rate + high R/R = Need discipline

3. **Fear Index >40%**: You're leaving money on table

4. **Most trades B grade or better**: Good efficiency

5. **Commission Impact >30%**: Trade less or bigger size

6. **Use Date Filters**: Track improvement over time

7. **Analyze by Symbol**: Stop trading consistent losers

8. **Review Extremes**: Learn from best/worst trades

9. **Check Holdings Dashboard**: Monitor unrealized P/L and sector allocation

10. **Watch Concentration**: Keep top 5 holdings < 60% of portfolio

---

## Open Position Tracking

**How it works:**
- Sums Quantity for each symbol
- If sum > 0: Open position
- If sum = 0: Closed

**Visual:**
- Yellow highlighting in symbol table
- `HasOpenPosition` column
- `OpenPosition` shows quantity

**Holdings Dashboard:**
- Full breakdown with cost basis
- Unrealized P/L tracking
- Sector allocation
- Live market prices

**Why it matters:**
- Track active positions
- Distinguish realized vs unrealized
- Risk management
- Portfolio rebalancing

---

## Troubleshooting

### No trades showing
- Check FifoPnlRealized ≠ 0
- Verify date filters

### Metrics seem wrong
- Remember: FifoPnlRealized is already NET
- Verify: Total P/L = sum(FifoPnlRealized)

### Charts not displaying
- Refresh page
- Check date filters

### Symbol shows open but seems closed
- Check Quantity sum
- Might have fractional shares

### Holdings Dashboard slow
- Normal: Fetches live prices from Yahoo Finance
- Typical: 1-2 seconds for 10 stocks
- Uses parallel fetching for speed

### Cost basis doesn't match IBKR
- Should match within $0.01
- Includes commissions (like IBKR)
- Uses FIFO accounting
- Check if all trades are in CSV

### "Unknown" sector for ETF
- Code attempts to get ETF category
- Some ETFs may not have sector data
- Manually verify ticker symbol is correct

---

## Validation Checklist

After upload, verify:

✅ Total P/L = sum of FifoPnlRealized  
✅ Total Fees = sum of IBCommission  
✅ Trades = rows with FifoPnlRealized ≠ 0  
✅ Win Rate in 30-70% range  
✅ Open positions highlighted yellow  
✅ Equity curve trends correctly  
✅ Holdings Dashboard cost basis matches IBKR  
✅ Unrealized P/L seems accurate  

---

## Important Notes

1. **FifoPnlRealized = Net P/L** (includes ALL commissions for closed trades)
2. **Don't add commissions** (already deducted from P/L)
3. **Cost Basis DOES include commissions** (this is correct for tax purposes)
4. **Open positions** (yellow highlighting, sum of Quantity > 0)
5. **Time-based charts** (calendar time, not trade #)
6. **All metrics** (based on closed trades only)
7. **Holdings Dashboard** (tracks open positions with live prices)

---

## Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] `pip install -r requirements.txt`
- [ ] `streamlit run app.py`
- [ ] Upload IBKR CSV
- [ ] Check Overview tab
- [ ] Review Performance charts
- [ ] Identify open positions (yellow in Symbol Analysis)
- [ ] **Check Holdings Dashboard for current portfolio**
- [ ] **Review sector allocation and concentration**
- [ ] Analyze time patterns
- [ ] Review best/worst trades
- [ ] Export data if needed

---

## Files Included

- `analyzer.py` - Analysis engine with FIFO cost basis
- `app.py` - Streamlit UI with 7 tabs
- `requirements.txt` - Dependencies (includes yfinance)
- `runner.bat` - Use it to run the app
- `README.md` - This file

---

**Ready to analyze! 📊**

Upload your CSV and discover:
- Trading performance patterns
- Behavioral issues (Fear Index)
- Which symbols to trade/avoid
- **Current portfolio allocation**
- **Unrealized gains/losses**
- **Sector diversification**
- Areas for improvement

For detailed metric explanations, scroll up to the "Metrics Explained" section. Everything you need to understand your complete trading picture is here!