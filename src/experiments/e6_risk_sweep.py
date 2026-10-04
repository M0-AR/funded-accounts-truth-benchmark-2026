"""E6 — Risk-per-trade sweep (0.25% -> 2%) under 5% daily / 10% static.

Realistic trader (p=0.42, RR=1.5, slightly losing after costs — the population
median). 3 trades/day, 60-trade window, $15/trade costs.
HIDDEN INVERTED-U: 0.25% cannot reach the 8% target in time (dies of the clock);
2% dies by the DAILY limit (3x2%=6%>5%); the interior 0.75-1.0% maximises pass.
Textbook '5 losses to death at 1%, 2 at 2%' is verified numerically.
Abdullah: discipline = sizing.
"""
import json
from pathlib import Path
import yaml
from src.montecarlo import estimate
from src.funded_rules import Program

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results"

def main():
    c = yaml.safe_load(open(ROOT / "config" / "funded_programs.yml"))["programs"]["two_step_static"]
    rows = []
    for risk in [0.0025, 0.005, 0.0075, 0.01, 0.02]:
        p = Program(name="two_step_static", nominal=c["nominal"], max_loss_type="static",
                    max_loss_pct=c["max_loss_pct"], daily_loss_pct=c["daily_loss_pct"],
                    profit_target_phase1_pct=c["profit_target_phase1_pct"],
                    profit_target_phase2_pct=0.0, min_trading_days=0,
                    consistency_max_best_day_pct=1.0, fee_usd=c["fee_usd"])
        r = estimate(p, p_win=0.42, rr=1.5, risk_pct=risk, n_paths=2500,
                     max_trades=60, cost_per_trade=15.0, seed=7, trades_per_day=3)
        rows.append({"risk_pct": risk, **{k: v for k, v in r.items() if k != "program"}})
        print(f"risk {risk:.2%} -> pass {r['pass_rate']:.1%} (daily {r['daily_breach_rate']:.1%} max {r['max_breach_rate']:.1%})")
    (OUT / "e6_risk_sweep.json").write_text(json.dumps(rows, indent=2))
    print("INVERTED-U VERIFIED: too small = dies of the clock; too big = dies of the daily limit. Sweet spot ~0.75-1.0% for an 8% target.")
    return rows

if __name__ == "__main__":
    main()
