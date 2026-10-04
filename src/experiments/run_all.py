"""Run the full benchmark end-to-end and emit results/summary.json + SUMMARY.md."""
import json
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results"

from src.experiments import (
    e1_effective_capital, e2_trailing_trap, e3_daily_stop,
    e4_overtrading, e5_models_compare, e6_risk_sweep,
    e7_consistency, e8_live_backtest, e9_fee_burn,
)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary, errors = {}, {}
    for name, fn in [
        ("e1", e1_effective_capital.main), ("e2", e2_trailing_trap.main),
        ("e3", e3_daily_stop.main), ("e4", e4_overtrading.main),
        ("e5", e5_models_compare.main), ("e6", e6_risk_sweep.main),
        ("e7", e7_consistency.main), ("e8", e8_live_backtest.main),
        ("e9", e9_fee_burn.main),
    ]:
        try:
            print(f"\n########## {name} ##########")
            summary[name] = fn()
        except Exception as e:
            errors[name] = traceback.format_exc()
            print(f"!!! {name} FAILED: {e}")
    (OUT / "summary.json").write_text(json.dumps(
        {"experiments": list(summary.keys()), "errors": list(errors.keys())}, indent=2))
    md = ["# Benchmark run summary", ""]
    for k in summary:
        md.append(f"- {k}: OK")
    for k, tb in errors.items():
        md.append(f"- {k}: FAILED\n```\n{tb[-2000:]}\n```")
    md += ["", "See results/e1_*.json ... e9_*.json for numbers. Re-run with `make all`.",
           "Data provenance: data/MANIFEST.txt (yahoo/stooq/synthetic-labelled)."]
    (OUT / "SUMMARY.md").write_text("\n".join(md))
    print("\n".join(md))
    if errors:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
