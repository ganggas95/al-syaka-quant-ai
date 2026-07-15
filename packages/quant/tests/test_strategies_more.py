import pandas as pd

from al_syaka_quant.strategies import BreakoutStrategy, RsiStrategy


def test_rsi_strategy_returns_signals():
    df = pd.DataFrame({"close": [100, 101, 102, 103, 104, 105, 106]})
    strategy = RsiStrategy(symbol="AAPL")
    signals = strategy.generate(df)
    assert signals
    assert signals[-1].action in {"buy", "sell", "hold"}


def test_breakout_strategy_returns_signals():
    df = pd.DataFrame({"close": [10, 11, 12, 13, 14, 15, 16]})
    strategy = BreakoutStrategy(symbol="EURUSD")
    signals = strategy.generate(df)
    assert signals
    assert signals[-1].action in {"buy", "sell", "hold"}
