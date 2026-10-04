"""Two trading behaviours straight from Abdullah's testimony.

disciplined (what he preaches AFTER blowing 40 accounts):
  - max 1 trade/day, risk 0.5% of nominal, ATR stop, TP = 1.5R
  - signal: close > SMA20 -> long else short (shifted 1 day, no lookahead)
  - NO Friday trading (manipulation / weekend-gap rule)
  - personal daily stop at 50% of firm daily limit (walk away)
  - max 3 trades/week? no — keep simple: 1/day + Friday off

reckless (what he DID 10:00-22:00 chart-staring era):
  - up to 5 trades/day (overtrading), risk 2% each
  - revenge: after a loss, double next risk (martingale-lite)
  - trades Fridays, no personal stop, holds through daily loss

Both use the SAME signal family so the ONLY difference is risk/discipline.
Costs: spread+commission per trade (default $12 per $100k-trade ~ 1.2bp round trip
is too kind; we use explicit cost_per_trade_usd on nominal-scaled size).

Trade PnL model (transparent, real-data-driven):
  R_raw = direction * (close - open) / ATR_prev
  pnl = clip(R_raw, -1, +1.5) * risk_usd - cost
where ATR_prev uses only past 14 days (no lookahead).
"""
from __future__ import annotations

import pandas as pd

LONG, SHORT, FLAT = 1, -1, 0


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    d["sma20"] = d["close"].rolling(20).mean()
    d["atr"] = (d["high"] - d["low"]).rolling(14).mean()
    d["prev_close"] = d["close"].shift(1)
    d["signal"] = 0
    d.loc[d["close"].shift(1) > d["sma20"].shift(1), "signal"] = LONG
    d.loc[d["close"].shift(1) <= d["sma20"].shift(1), "signal"] = SHORT
    # no-lookahead: signal for day t uses only data up to t-1 (shifted above)
    return d


def daily_trade_pnl(direction: int, row, risk_usd: float, cost: float,
                    tp_r: float = 1.5) -> float:
    atr = float(row["atr"])
    if not atr or atr <= 0 or pd.isna(atr):
        return 0.0
    move = float(row["close"] - row["open"])
    r = direction * move / atr
    r = max(-1.0, min(tp_r, r))
    return r * risk_usd - cost


def generate_day_trades(style: str, feat: pd.DataFrame, nominal: float,
                        base_risk_pct: float, cost_per_trade: float):
    """Yield (date, direction, risk_usd, tag) tuples in chronological order."""
    risk_base = nominal * base_risk_pct
    revenge_mult = 1.0
    for date, row in feat.iterrows():
        if pd.isna(row["atr"]) or pd.isna(row["signal"]):
            continue
        weekday = date.weekday()  # 4 = Friday
        if style == "disciplined":
            if weekday == 4:
                revenge_mult = 1.0
                continue
            yield (date, int(row["signal"]), risk_base, "steady")
        elif style == "reckless":
            n = 5  # overtrading: 5 stares at the screen
            for k in range(n):
                # revenge sizing: alternate direction chase (noise) — keep same signal
                # but scale risk by revenge multiplier
                yield (date, int(row["signal"]), risk_base * revenge_mult, f"over{k}")
            # revenge update handled by caller via last pnl sign; expose hook:
            # (caller sets generate_day_trades.revenge flag — simpler: stateless doubling
            #  approximated by alternating 1x/2x; exact revenge loop lives in backtest)
        else:
            raise ValueError(style)
