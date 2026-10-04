"""Monte-Carlo challenge simulator: why the industry pass rate is 6-17%.

Each trade: win with p -> +RR*R, else -R, where R = risk_pct * nominal.
Costs subtracted per trade. After each trade we update balance AND the
trailing floor / daily bucket using the same FundedAccount engine, so the
simulation respects ratchets, daily limits, consistency and min-days —
not just terminal P&L.

Used by E3/E5/E6/E9. Seeded (numpy Generator) for full reproducibility.
"""
from __future__ import annotations

import numpy as np

from .funded_rules import FundedAccount, Program


def simulate_one(prog: Program, p_win: float, rr: float, risk_pct: float,
                 max_trades: int, cost_per_trade: float, rng: np.random.Generator,
                 trades_per_day: int = 2) -> dict:
    acct = FundedAccount(prog)
    R = prog.nominal * risk_pct
    day_counter = 0
    day_trades = 0
    prev_bal = prog.nominal
    acct.start_day(prev_bal, prev_bal)
    for t in range(max_trades):
        if day_trades >= trades_per_day:
            acct.end_day(acct.balance)
            day_counter += 1
            prev_bal = acct.balance
            acct.start_day(prev_bal, prev_bal)
            day_trades = 0
        win = rng.random() < p_win
        pnl = (rr * R - cost_per_trade) if win else (-R - cost_per_trade)
        eq = acct.balance + pnl  # closed-trade equity == balance here
        b = acct.apply_pnl(pnl, eq, f"d{day_counter}", is_close=True)
        day_trades += 1
        if b:
            acct.end_day(acct.balance)
            break
    else:
        acct.end_day(acct.balance)
    ok, reason = acct.passes_target(phase=1)
    return {"pass": ok, "reason": reason, "profit_pct": acct.profit_pct(),
            "breach": acct.breached, "best_day": acct.best_day_share(),
            "days": len(acct.traded_days)}


def estimate(prog: Program, p_win: float, rr: float, risk_pct: float,
             n_paths: int = 4000, max_trades: int = 60,
             cost_per_trade: float = 12.0, seed: int = 42,
             trades_per_day: int = 2) -> dict:
    rng = np.random.Generator(np.random.PCG64(seed))
    passes, breaches_daily, breaches_max = 0, 0, 0
    for _ in range(n_paths):
        r = simulate_one(prog, p_win, rr, risk_pct, max_trades,
                         cost_per_trade, rng, trades_per_day)
        passes += r["pass"]
        if "daily" in r["breach"]:
            breaches_daily += 1
        elif "max_loss" in r["breach"]:
            breaches_max += 1
    return {"program": prog.name, "n": n_paths, "pass_rate": passes / n_paths,
            "daily_breach_rate": breaches_daily / n_paths,
            "max_breach_rate": breaches_max / n_paths,
            "p_win": p_win, "rr": rr, "risk_pct": risk_pct}
