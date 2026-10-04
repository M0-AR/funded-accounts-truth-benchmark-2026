"""E7 — Consistency / best-day rule: hero day vs steady grind.

Same +6% total, two paths:
  hero:  +5% in one day, +1% rest  -> best-day share 83% -> FAILS 50% rule
  steady: +1% x6 days             -> best-day share ~17% -> PASSES
This is why Mo'men warns: passing the TARGET is not passing the RULES.
"""
import json
from pathlib import Path
from src.funded_rules import FundedAccount, Program

OUT = Path(__file__).resolve().parents[2] / "results"

def run(daily):
    prog = Program(name="two_step_static", nominal=100_000, max_loss_type="static",
                   max_loss_pct=0.10, daily_loss_pct=0.05,
                   profit_target_phase1_pct=0.06, min_trading_days=3,
                   consistency_max_best_day_pct=0.50)
    a = FundedAccount(prog)
    bal = 100_000
    for i, pct in enumerate(daily):
        pnl = pct * 100_000
        a.start_day(bal, bal)
        a.apply_pnl(pnl, bal + pnl, f"d{i}")
        a.end_day(bal + pnl)
        bal += pnl
    ok, reason = a.passes_target(1)
    return {"daily": daily, "profit": a.profit_pct(), "best_day": round(a.best_day_share(), 3),
            "pass": ok, "reason": reason}

def main():
    hero = run([0.05, 0.005, 0.005, 0.0])
    steady = run([0.01, 0.01, 0.01, 0.01, 0.01, 0.01])
    out = {"hero_day": hero, "steady_grind": steady}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e7_consistency.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    print("LESSON: size for repeatability, not for one screenshot day.")
    return out

if __name__ == "__main__":
    main()
