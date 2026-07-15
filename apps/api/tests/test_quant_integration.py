import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.unified_signal import UnifiedSignalGenerator


def test_build_quant_signal_uses_mean_reversion_strategy():
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    df = pd.DataFrame({"close": [1.10, 1.12, 1.11, 1.09, 1.08, 1.07, 1.06]})

    quant_signal = generator._build_quant_signal(df, "EURUSD")

    assert quant_signal["strategy"] == "MeanReversionStrategy"
    assert quant_signal["action"] in {"buy", "sell"}
    assert 0.0 <= quant_signal["confidence"] <= 1.0
