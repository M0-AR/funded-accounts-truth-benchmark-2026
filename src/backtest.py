"""Event-driven backtest under the funded rule wrapper.

Pseudocode per symbol:
  feat = add_features(df)
  acct.start_day(nominal, nominal)
  for each day:
    acct.start_day(prev_close_balance, prev_close_equity)
    for each trade (1 for disciplined, 5 for reckless):
      pnl = daily_trade_pnl(...) / n_trades split (reckless splits the day move)
      equity_now = balance + floating(0 at close) -> balance+pnl path
      breach = acct.apply_pnl(pnl_slice, equity_now, date)
      if breach: stop everything
    acct.end_day(balance)
    personal stop: disciplined quits the DAY if day_pnl <= -0.5*firm_daily
    reckless never quits (revenge doubles next day risk)

Reckless day-move split: the same (close-open) move divided into 5 slices with
alternating noise so overtrading pays 5x costs for the same gross edge.
Revenge: if previous DAY lost, next day risk x2 (capped x4).

Returns BacktestResult with full audit trail.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .funded_rules import FundedAccount, Program
from .strategies import add_features, daily_trade_pnl


@dataclass
class BacktestResult:
    symbol: str
    style: str
    program: str
    nominal: float
    end_balance: float
    profit_pct: float
    breached: str
    n_trades: int
    n_days: int
    win_rate: float
    profit_factor: float
    best_day_share: float
    max_equity_dd_pct: float
    equity_curve: list = field(default_factory=list)
    daily_pnls: list = field(default_factory=list)


def run_symbol(df: pd.DataFrame, symbol: str, style: str, prog: Program,
               base_risk_pct: float, cost_per_trade: float) -> BacktestResult:
    feat = add_features(df)
    acct = FundedAccount(prog)
    n_trades, wins, gross_win, gross_loss = 0, 0, 0.0, 0.0
    peak_eq, max_dd = prog.nominal, 0.0
    equity_curve = []
    prev_balance = prog.nominal
    revenge_mult = 1.0

    for date, row in feat.iterrows():
        if pd.isna(row["atr"]) or int(row["signal"]) == 0:
            equity_curve.append(acct.balance)
            continue
        ds = date.strftime("%Y-%m-%d")
        is_friday = date.weekday() == 4
        if style == "disciplined" and is_friday:
            acct.start_day(prev_balance, prev_balance)
            acct.end_day(acct.balance)
            prev_balance = acct.balance
            equity_curve.append(acct.balance)
            continue
        # day setup
        acct.start_day(prev_balance, prev_balance)
        firm_daily_amt = prog.nominal * prog.daily_loss_pct
        personal_stop = -0.5 * firm_daily_amt if style == "disciplined" else float("inf")
        n_today = 1 if style == "disciplined" else 5
        risk_today = prog.nominal * base_risk_pct * revenge_mult
        day_pnl_acc = 0.0
        for k in range(n_today):
            direction = int(row["signal"])
            # split move across slices for reckless so gross edge is comparable
            full = daily_trade_pnl(direction, row, risk_today, cost_per_trade)
            pnl = full if n_today == 1 else full / n_today - (cost_per_trade * 0.8)
            # NOTE: reckless pays ~5x costs: full/5 minus extra cost each slice
            eq_now = acct.balance + day_pnl_acc + pnl
            b = acct.apply_pnl(pnl, eq_now, ds, is_close=True)
            n_trades += 1
            day_pnl_acc += pnl
            if pnl > 0:
                wins += 1
                gross_win += pnl
            else:
                gross_loss += -pnl
            peak_eq = max(peak_eq, eq_now)
            max_dd = max(max_dd, (peak_eq - eq_now) / peak_eq)
            if b:
                break
            if style == "disciplined" and day_pnl_acc <= -personal_stop * 0 + (-0.5 * firm_daily_amt):
                # personal stop hit (half the firm limit) -> walk away
                if day_pnl_acc <= -0.5 * firm_daily_amt:
                    break
        acct.end_day(acct.balance)
        prev_balance = acct.balance
        equity_curve.append(acct.balance)
        if acct.breached:
            break
        # revenge update: reckless doubles after red day (cap x4), disciplined resets
        if style == "reckless":
            revenge_mult = min(4.0, revenge_mult * 2.0) if day_pnl_acc < 0 else 1.0

    pf = (gross_win / gross_loss) if gross_loss > 0 else (float("inf") if gross_win > 0 else 0.0)
    wr = wins / n_trades if n_trades else 0.0
    return BacktestResult(
        symbol=symbol, style=style, program=prog.name, nominal=prog.nominal,
        end_balance=acct.balance, profit_pct=acct.profit_pct(),
        breached=acct.breached, n_trades=n_trades,
        n_days=len(acct.traded_days), win_rate=wr,
        profit_factor=float(pf) if pf != float("inf") else 999.0,
        best_day_share=acct.best_day_share(),
        max_equity_dd_pct=max_dd * 100,
        equity_curve=equity_curve, daily_pnls=list(acct.daily_pnls),
    )
