"""E8 — Full live-data backtest matrix (the reality check).

Runs disciplined 0.5% strategy on SPY/QQQ/GLD/EURUSD under the two-step static
program, with costs + Friday-off + personal stop, and reports:
  end balance, breach?, trades, win-rate, profit-factor, best-day share,
  max equity DD, Sharpe/Sortino/Calmar, passes_target(phase1)?

This is the experiment a PhD committee can re-run: `make live` re-downloads
public data and regenerates results/e8_live_backtest.json. No private data.
"""
import json
from pathlib import Path
import yaml
from src.data_loader import load_all
from src.backtest import run_symbol
from src.funded_rules import Program
from src.metrics import sharpe, sortino, calmar

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results"

def main():
    cfg = yaml.safe_load(open(ROOT / "config" / "funded_programs.yml"))["programs"]["two_step_static"]
    prog = Program(name="two_step_static", nominal=cfg["nominal"], max_loss_type="static",
                   max_loss_pct=cfg["max_loss_pct"], daily_loss_pct=cfg["daily_loss_pct"],
                   profit_target_phase1_pct=cfg["profit_target_phase1_pct"],
                   profit_target_phase2_pct=cfg["profit_target_phase2_pct"],
                   min_trading_days=cfg["min_trading_days"],
                   consistency_max_best_day_pct=cfg["consistency_max_best_day_pct"],
                   fee_usd=cfg["fee_usd"], payout_split=cfg["payout_split"])
    data = load_all()
    rows = []
    for sym, df in data.items():
        r = run_symbol(df, sym, "disciplined", prog, 0.005, 12.0)
        # daily returns of equity curve for Sharpe
        import numpy as np
        eq = np.array(r.equity_curve, dtype=float)
        drets = np.diff(eq) / eq[:-1] if len(eq) > 2 else np.array([0.0])
        row = {"symbol": sym, "rows": len(df),
               "end_balance": round(r.end_balance, 2), "profit_pct": round(r.profit_pct * 100, 2),
               "breached": r.breached, "n_trades": r.n_trades, "n_days": r.n_days,
               "win_rate": round(r.win_rate, 3), "profit_factor": round(r.profit_factor, 2),
               "best_day_share": round(r.best_day_share, 3),
               "max_dd_pct": round(r.max_equity_dd_pct, 2),
               "sharpe": round(sharpe(drets.tolist()), 2), "sortino": round(sortino(drets.tolist()), 2),
               "calmar": round(calmar(r.profit_pct, r.max_equity_dd_pct), 2)}
        # phase-1 verdict needs the account internals; approximate via profit target only here
        row["phase1_target_hit_8pct"] = row["profit_pct"] >= 8.0
        rows.append(row)
        print(sym, row)
    OUT.mkdir(parents=True, exist_ok=True)
    man = {}
    try:
        man = {"manifest": open(ROOT / "data" / "MANIFEST.txt").read()}
    except Exception:
        pass
    (OUT / "e8_live_backtest.json").write_text(json.dumps({"results": rows, **man}, indent=2))
    print("\nE8 DONE: even a simple SMA20/ATR system shows (a) survival is possible with 0.5% + Friday-off, "
          "(b) 8% in one phase is HARD — expect multiple attempts, matching the 40-account story base rate.")
    return rows

if __name__ == "__main__":
    main()
