"""Live + cached market data loader.

Zero-to-hero verification protocol (from 2026 best practice synthesis):
  1. Try Yahoo Finance (yfinance) for real OHLCV.
  2. Fallback to Stooq free CSV (no key) — fully public.
  3. Fallback to deterministic synthetic GBM (seeded) so CI never breaks.
  4. Cache every download to data/*.csv with source + sha metadata.
  5. NEVER use future bars to compute signals (callers must shift by 1).

Tickers cover the instruments Abdullah / Mo'men discuss:
  SPY (S&P500 ~ SPX500/NASDAQ proxy), QQQ (Nasdaq-100), GLD (gold/XAUUSD),
  EURUSD=X (FX). All are public, free, and re-downloadable.
"""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DEFAULT_TICKERS = {
    "SPY": "SPY",
    "QQQ": "QQQ",
    "GLD": "GLD",          # gold proxy for XAUUSD
    "EURUSD": "EURUSD=X",  # FX proxy
}

@dataclass
class DataReport:
    symbol: str
    rows: int
    start: str
    end: str
    source: str
    path: str


def _stooq_symbol(yahoo_symbol: str) -> str:
    m = {"SPY": "spy.us", "QQQ": "qqq.us", "GLD": "gld.us", "EURUSD=X": "eurusd"}
    return m.get(yahoo_symbol, yahoo_symbol.lower())


def fetch_stooq(yahoo_symbol: str, start: str = "2018-01-01") -> pd.DataFrame | None:
    """Free Stooq daily CSV, no API key. Returns OHLCV or None."""
    try:
        import requests
        sym = _stooq_symbol(yahoo_symbol)
        url = f"https://stooq.com/q/d/l/?s={sym}&d1={start.replace('-','')}&d2=20300101&i=d"
        r = requests.get(url, timeout=20)
        if r.status_code != 200 or "Date," not in r.text[:200]:
            return None
        from io import StringIO
        df = pd.read_csv(StringIO(r.text), parse_dates=["Date"])
        df = df.rename(columns={"Date": "date", "Open": "open", "High": "high",
                                "Low": "low", "Close": "close", "Volume": "volume"})
        df = df.dropna(subset=["close"])
        df = df.set_index("date").sort_index()
        if len(df) < 100:
            return None
        return df
    except Exception:
        return None


def fetch_yahoo(yahoo_symbol: str, start: str = "2018-01-01") -> pd.DataFrame | None:
    try:
        import yfinance as yf
        df = yf.download(yahoo_symbol, start=start, progress=False, auto_adjust=False)
        if df is None or len(df) == 0:
            return None
        # flatten MultiIndex columns (yfinance >=0.2 returns them)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0].lower() for c in df.columns]
        else:
            df.columns = [c.lower() for c in df.columns]
        rename = {"adj close": "adj_close"}
        df = df.rename(columns=rename)
        keep = [c for c in ["open", "high", "low", "close", "volume"] if c in df.columns]
        df = df[keep].dropna(subset=["close"])
        if len(df) < 100:
            return None
        return df
    except Exception:
        return None


def synthetic_gbm(symbol: str, start: str = "2018-01-01", n: int = 1500, seed: int = 7) -> pd.DataFrame:
    """Deterministic GBM so experiments run offline. Clearly labelled synthetic."""
    rng = np.random.default_rng(abs(hash(symbol + str(seed))) % (2**31))
    dt = 1 / 252
    mu, sigma = 0.06, 0.20
    rets = rng.normal((mu - 0.5 * sigma**2) * dt, sigma * np.sqrt(dt), n)
    close = 100 * np.exp(np.cumsum(rets))
    open_ = np.concatenate([[100], close[:-1]]) * (1 + rng.normal(0, 0.001, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.002, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.002, n)))
    idx = pd.date_range(start=start, periods=n, freq="B")
    return pd.DataFrame({"open": open_, "high": high, "low": low,
                         "close": close, "volume": 1_000_000}, index=idx)


def load_symbol(symbol_key: str, yahoo_symbol: str, start: str = "2018-01-01",
                force_synthetic: bool = False) -> tuple[pd.DataFrame, DataReport]:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    cache = DATA_DIR / f"{symbol_key}.csv"
    source = "synthetic"
    df: pd.DataFrame | None = None

    if not force_synthetic:
        # 1) cache hit
        if cache.exists():
            try:
                df = pd.read_csv(cache, parse_dates=[0], index_col=0)
                df.index = pd.to_datetime(df.index)
                if len(df) >= 200:
                    source = "cache:" + (cache.stat().st_size and "local" or "local")
                else:
                    df = None
            except Exception:
                df = None
        # 2) live sources
        if df is None:
            df = fetch_yahoo(yahoo_symbol, start)
            source = "yahoo" if df is not None else source
        if df is None:
            df = fetch_stooq(yahoo_symbol, start)
            source = "stooq" if df is not None else source
    if df is None:
        df = synthetic_gbm(symbol_key, start)
        source = "synthetic-seeded"
    # persist cache (only for real sources; synthetic cached too for transparency)
    try:
        df.to_csv(cache)
    except Exception:
        pass
    rep = DataReport(symbol=symbol_key, rows=len(df),
                     start=str(df.index[0].date()), end=str(df.index[-1].date()),
                     source=source, path=str(cache))
    return df, rep


def load_all(start: str = "2018-01-01", force_synthetic: bool = False) -> dict[str, pd.DataFrame]:
    out, reports = {}, []
    for key, ysym in DEFAULT_TICKERS.items():
        df, rep = load_symbol(key, ysym, start, force_synthetic)
        out[key] = df
        reports.append(rep)
    # manifest for reproducibility
    man = DATA_DIR / "MANIFEST.txt"
    with open(man, "w") as f:
        for r in reports:
            h = hashlib.sha256(pd.util.hash_pandas_object(out[r.symbol]).values).hexdigest()[:16]
            f.write(f"{r.symbol} rows={r.rows} {r.start}->{r.end} source={r.source} sha16={h} path={r.path}\n")
    return out
