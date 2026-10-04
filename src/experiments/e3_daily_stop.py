"""E3 — Daily-loss micro-breach + personal stop (Mo'men secret #3).

Firm: 5% daily on 100k ($5k). Compare:
  A) trader stops at firm limit (5x 1% losses = death)
  B) trader uses personal stop at 2.5% (Abdullah-style: walk away early)
Monte-Carlo with p=0.45, RR=1.5, risk 1%/trade, 4 trades/day, 20 days.
Metric: breach rate + median surviving days.
"""
import json
from pathlib import Path
import numpy as np
from src.funded_rules import FundedAccount, Program

OUT = Path(__file__).resolve().parents[2] / "results"

def simulate(personal_pct: float, seed: int = 1, n: int = 3000):
    prog = Program(name="t", nominal=100_000, max_loss_type="static",
                   max_loss_pct=0.10, daily_loss_pct=0.05)
    rng = np.random.Generator(np.random.PCG64(seed))
    breaches = 0
    for _ in range(n):
        a = FundedAccount(prog)
        bal = 100_000
        dead = False
        for _d in range(20):
            a.start_day(bal, bal)
            for _t in range(4):
                win = rng.random() < 0.45
                pnl = 1500 - 12 if win else -1000 - 12
                eq = a.balance + pnl if False else a.balance + pnl  # closed
                # personal stop checked BEFORE next trade
                if a.day_pnl + pnl <= -personal_pct * 100_000 and personal_pct < 0.05:
                    # stop out for the day: book this trade then quit day
                    b = a.apply_pnl(pnl, a.balance + a.day_pnl + pnl, "d")
                    if b:
                        dead = True
                    break
                b = a.apply_pnl(pnl, a.balance + a.day_pnl + pnl, "d")
                if b:
                    dead = True
                    break
            a.end_day(a.balance)
            bal = a.balance
            if dead or a.breached:
                break
        if a.breached:
            breaches += 1
    return breaches / n

def main():
    r_firm = simulate(0.05, seed=11)
    r_personal = simulate(0.025, seed=11)
    out = {"breach_at_firm_limit_5pct": r_firm,
           "breach_with_personal_stop_2.5pct": r_personal,
           "relative_reduction_pct": round((r_firm - r_personal) / max(r_firm, 1e-9) * 100, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e3_daily_stop.json").write_text(json.dumps(out, indent=2))
    print("== E3 daily stop ==", out)
    print("RULE: firm limit is the CLIFF, personal stop (<=50-60% of it) is the PLAN.")
    return out

if __name__ == "__main__":
    main()
