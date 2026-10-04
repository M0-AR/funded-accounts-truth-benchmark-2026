"""E2 — The trailing trap (Mo'men secret #2 + Abdullah's 2-step preference).

Same equity path under three floors:
  static 10%  | trailing-EOD 10% | trailing-intraday 10%
Path: 100k -> 105k (peak) -> 96k pullback -> 102k.
Static survives (floor 90k). Trailing-EOD floor rose to 95k -> survives barely.
Intraday with a 107k wick -> floor 97k -> the SAME 96k close breaches.

Also sweeps a second path: steady grind +7% then -8% intraday spike.
"""
import json
from pathlib import Path
from src.funded_rules import FundedAccount, Program

OUT = Path(__file__).resolve().parents[2] / "results"

def run_path(ptype: str, closes: list[float], wick: float | None = None):
    prog = Program(name=ptype, nominal=100_000, max_loss_type=ptype,
                   max_loss_pct=0.10, daily_loss_pct=0.99)  # disable daily for isolation
    a = FundedAccount(prog)
    a.start_day(100_000, 100_000)
    eq = 100_000
    for c in closes:
        pnl = c - eq
        eq = c
        if wick and c == max(closes):
            # intraday wick prints a higher equity high first
            b = a.apply_pnl(wick - (eq - pnl), wick, "d", is_close=False)
            if b:
                return {"breached": b, "floor": a.floor}
        b = a.apply_pnl(pnl, eq, "d", is_close=True)
        if b:
            return {"breached": b, "floor": a.floor}
        a.end_day(a.balance)
        a.start_day(a.balance, a.balance)
    return {"breached": "", "floor": a.floor, "end": a.balance}

def main():
    path = [102_000, 105_000, 96_000, 102_000]
    out = {}
    for t in ["static", "trailing_eod", "trailing_intraday"]:
        out[t] = run_path(t, path, wick=107_000 if t == "trailing_intraday" else None)
    # grind path
    grind = [101_000, 103_000, 107_000, 99_000]
    out["grind_static"] = run_path("static", grind)
    out["grind_trailing_eod"] = run_path("trailing_eod", grind)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e2_trailing_trap.json").write_text(json.dumps(out, indent=2))
    print("== E2 trailing trap ==")
    print(json.dumps(out, indent=2))
    print("\nCONCLUSION: profit RAISES the floor under trailing; the same pullback "
          "that static absorbs can kill a trailing account. Prefer static/EOD for learning (Abdullah right).")
    return out

if __name__ == "__main__":
    main()
