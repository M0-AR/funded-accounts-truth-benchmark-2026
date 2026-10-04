"""No-lookahead + data integrity tests."""
import pandas as pd
from src.strategies import add_features
from src.data_loader import synthetic_gbm

def test_signal_uses_only_past():
    df = synthetic_gbm("TEST", n=100, seed=3)
    f = add_features(df)
    # signal on day t must equal function of closes up to t-1:
    # recompute manually for row 50
    i = 50
    sma20_past = df["close"].iloc[i-20:i].mean()
    expected = 1 if df["close"].iloc[i-1] > sma20_past else -1
    assert int(f["signal"].iloc[i]) == expected

def test_synthetic_deterministic():
    a = synthetic_gbm("X", n=50, seed=9)
    b = synthetic_gbm("X", n=50, seed=9)
    pd.testing.assert_frame_equal(a, b)

def test_atr_needs_history():
    df = synthetic_gbm("Y", n=30, seed=1)
    f = add_features(df)
    assert pd.isna(f["atr"].iloc[5])
    assert not pd.isna(f["atr"].iloc[20])
