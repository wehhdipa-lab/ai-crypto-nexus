# Trading Strategies

## Available Strategies

### 1. Momentum (LSTM-based)
ML momentum strategy using LSTM with attention mechanism.

**Features**: RSI, MACD, volume ratio, price range, volatility
**Signal**: Buy when momentum score > threshold, sell when < -threshold

```python
from nexus.trading.strategies.momentum import MomentumStrategy
strategy = MomentumStrategy(lookback=60, threshold=0.6)
signals = strategy.generate_signals(ohlcv_data)
```

### 2. Sentiment (NLP)
Crypto-specific sentiment analysis using custom lexicon.

```python
from nexus.trading.strategies.sentiment import SentimentStrategy
score = SentimentStrategy.analyze_text("ETH is mooning!")  # > 0
```

### 3. Mean Reversion (Z-Score)
Statistical mean reversion using z-scores.

```python
from nexus.trading.strategies.mean_reversion import MeanReversionStrategy
strategy = MeanReversionStrategy(z_entry=2.0)
signals = strategy.generate_signals(ohlcv_data)
```

## Backtesting

```python
from nexus.trading.backtester import Backtester, BacktestConfig

config = BacktestConfig(
    initial_capital=100000,
    slippage_bps=30,
    gas_per_trade=5.0,
)

bt = Backtester(config)
result = bt.run(strategy, data)
print(f"Return: {result.total_return:.1f}%")
print(f"Sharpe: {result.sharpe_ratio:.2f}")
print(f"Max DD: {result.max_drawdown:.1f}%")
print(f"Win Rate: {result.win_rate:.0f}%")
```

## Risk Management

```python
from nexus.trading.risk import RiskManager

# Optimal position size
kelly = RiskManager.kelly_fraction(win_rate=0.6, avg_win=0.05, avg_loss=0.03)
size = RiskManager.position_size(100000, kelly, entry=3500, stop=3325)

# Value at Risk
var = RiskManager.value_at_risk(returns, confidence=0.95, horizon=7)
```
