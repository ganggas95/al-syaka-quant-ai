"""Session-based features: Asian, London, US sessions."""

import pandas as pd
import numpy as np
from datetime import time


def _is_session(timestamp, session_start, session_end):
    """Check if timestamp falls within a trading session."""
    t = timestamp.time()
    if session_start <= session_end:
        return session_start <= t <= session_end
    else:  # Overnight session
        return t >= session_start or t <= session_end


def session_features(timestamps: pd.DatetimeIndex | pd.Series) -> dict:
    """Extract trading session features."""
    asian_session = timestamps.map(lambda ts: _is_session(ts, time(0, 0), time(9, 0)))
    london_session = timestamps.map(lambda ts: _is_session(ts, time(8, 0), time(17, 0)))
    us_session = timestamps.map(lambda ts: _is_session(ts, time(13, 0), time(22, 0)))
    london_open = timestamps.map(lambda ts: _is_session(ts, time(8, 0), time(9, 0)))
    us_open = timestamps.map(lambda ts: _is_session(ts, time(13, 30), time(14, 30)))
    session_overlap = (london_session & us_session).astype(int)

    return {
        "asian_session": asian_session.astype(int),
        "london_session": london_session.astype(int),
        "us_session": us_session.astype(int),
        "london_open": london_open.astype(int),
        "us_open": us_open.astype(int),
        "session_overlap": session_overlap,
    }
