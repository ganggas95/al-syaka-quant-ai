import pandas as pd

from al_syaka_quant.backtest import run_backtest
from al_syaka_quant.strategies import MeanReversionStrategy


def test_mean_reversion_strategy_returns_signals():
    df = pd.DataFrame({"close": [1.10, 1.12, 1.11, 1.09, 1.08, 1.07, 1.06, 1.05, 1.06, 1.08]})
    strategy = MeanReversionStrategy(symbol="EURUSD", window=3)

    result = run_backtest(strategy, df)

    assert result["strategy"] == "MeanReversionStrategy"
    assert result["signal_count"] > 0
    assert result["signals"][0]["symbol"] == "EURUSD"
