import backtrader as bt
import yfinance as yf
import pandas as pd

# --- STRATEGIES ---
class SMACross(bt.Strategy):
    params = (('pfast', 10), ('pslow', 30),)
    def __init__(self):
        self.sma1 = bt.ind.SMA(period=self.params.pfast)
        self.sma2 = bt.ind.SMA(period=self.params.pslow)
        self.crossover = bt.ind.CrossOver(self.sma1, self.sma2)
    def next(self):
        if not self.position and self.crossover > 0: self.buy()
        elif self.crossover < 0: self.close()

class RSIStrategy(bt.Strategy):
    params = (('upper', 70), ('lower', 30), ('period', 14),)
    def __init__(self): self.rsi = bt.ind.RSI(period=self.params.period)
    def next(self):
        if not self.position and self.rsi < self.params.lower: self.buy()
        elif self.rsi > self.params.upper: self.close()

class BBandsStrategy(bt.Strategy):
    params = (('period', 20), ('devfactor', 2.0),)
    def __init__(self): self.bb = bt.ind.BollingerBands(period=self.params.period, devfactor=self.params.devfactor)
    def next(self):
        if not self.position and self.data.close < self.bb.lines.bot: self.buy()
        elif self.data.close > self.bb.lines.top: self.close()

# --- MAIN ENGINE ---
def run_comparison(ticker_symbol):
    print(f"--- Technical Analysis Backtester ---")
    print(f"Requesting data for: {ticker_symbol}...")

    # Fetch data with specific settings to avoid MultiIndex issues
    df = yf.download(ticker_symbol, start="2023-01-01", end="2023-12-31", progress=False)

    # 1. Check if data actually exists
    if df.empty:
        print(f"Error: No data found for {ticker_symbol}. Check your internet or ticker.")
        return

    # 2. Fix MultiIndex columns (Flatten the columns)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    strategies = [
        (SMACross, "SMA Crossover"),
        (RSIStrategy, "RSI Strategy"),
        (BBandsStrategy, "Bollinger Bands")
    ]
    
    final_results = []

    for strat_class, name in strategies:
        cerebro = bt.Cerebro()
        
        # Add data
        data = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data)
        
        # Add strategy and broker settings
        cerebro.addstrategy(strat_class)
        cerebro.broker.setcash(10000.0)
        cerebro.broker.setcommission(commission=0.001)
        
        initial = cerebro.broker.getvalue()
        cerebro.run()
        final = cerebro.broker.getvalue()
        
        profit = final - initial
        final_results.append((name, final, profit))
        print(f"Finished {name}...")

    # --- FINAL OUTPUT TABLE ---
    print("\n" + "="*45)
    print(f"{'STRATEGY':<20} | {'FINAL VALUE':<12} | {'PROFIT'}")
    print("-" * 45)
    for name, val, profit in final_results:
        print(f"{name:<20} | ${val:<11.2f} | ${profit:.2f}")
    print("="*45)

if __name__ == "__main__":
    run_comparison("AAPL")