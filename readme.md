# 📊 Trading Performance Analyzer Pro

A comprehensive trading analytics tool for analyzing IBKR (Interactive Brokers) trade data. Get deep insights into your trading performance with advanced metrics, visualizations, and behavioral analysis.

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
- **Open Position Tracking** (blue highlighting)
- Win rate, best/worst trades per symbol

### Time Analysis
- Day of week performance
- Monthly tracking
- Top 5 winners/losers

### Interactive Features
- Date and symbol filters
- 6 organized tabs
- Export to CSV
- Professional charts

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

### 6 Tabs Explained

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
  - >2.0 = Excellent
  
- **Expectancy** (Average $ per trade)
  - Positive = Profitable strategy
  - Higher = Better
  
- **R/R Ratio** (Avg Win ÷ Avg Loss)
  - <1.5 = Below average
  - 1.5-2.5 = Good
  - >2.5 = Excellent

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
- **Blue = Open position** (Quantity sum > 0)
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
- >60%: 🚨 Severe psychological issue

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
- >3.0: ✅ Excellent

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
- >2.5: ✅ Excellent

**Key:** You can be profitable with 40% win rate if R/R > 2:1

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
- >30%: 🚨 Very high risk

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
- >50%: 🚨 Overtrading

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

---

## Open Position Tracking

**How it works:**
- Sums Quantity for each symbol
- If sum > 0: Open position
- If sum = 0: Closed

**Visual:**
- Blue highlighting in symbol table
- `HasOpenPosition` column
- `OpenPosition` shows quantity

**Why it matters:**
- Track active positions
- Distinguish realized vs unrealized
- Risk management

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

---

## Validation Checklist

After upload, verify:

✅ Total P/L = sum of FifoPnlRealized  
✅ Total Fees = sum of IBCommission  
✅ Trades = rows with FifoPnlRealized ≠ 0  
✅ Win Rate in 30-70% range  
✅ Open positions highlighted yellow  
✅ Equity curve trends correctly  

---

## Important Notes

1. **FifoPnlRealized = Net P/L** (includes ALL commissions)
2. **Don't add commissions** (already deducted)
3. **Open positions** (yellow, Quantity sum > 0)
4. **Time-based charts** (calendar time, not trade #)
5. **All metrics** (closed trades only)

---

## Quick Start Checklist

- [ ] Install Python 3.8+
- [ ] `pip install -r requirements.txt`
- [ ] `streamlit run app.py`
- [ ] Upload IBKR CSV
- [ ] Check Overview tab
- [ ] Review Performance charts
- [ ] Identify open positions (yellow)
- [ ] Analyze time patterns
- [ ] Review best/worst trades
- [ ] Export data if needed

---

## Files Included

- `analyzer.py` - Analysis engine
- `app.py` - Streamlit UI
- `requirements.txt` - Dependencies
- `README.md` - This file

---

**Ready to analyze! 📊**

Upload your CSV and discover patterns, strengths, and areas to improve in your trading strategy.

For detailed metric explanations, scroll up to the "Metrics Explained" section. Everything you need to understand your performance is here!
