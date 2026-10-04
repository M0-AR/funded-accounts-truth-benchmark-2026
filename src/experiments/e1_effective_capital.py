"""E1 — Nominal vs effective capital (Mo'men secret #1).

Claim: '$100k account' with 10% max loss = $10k real risk capital.
An 8% nominal target = 80% on effective capital. A $500 fee = 5% of
effective capital per attempt. Small accounts can be kinder because the
RATIO matters more than the headline.

Writes results/e1_effective_capital.json + prints table.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "results"

CASES = [
    ("two_step_static 100k/10%", 100_000, 0.10, 500, 0.08),
    ("two_step_static 25k/10%", 25_000, 0.10, 150, 0.08),
    ("one_step 100k/6%", 100_000, 0.06, 600, 0.10),
    ("instant 100k/5%", 100_000, 0.05, 900, 0.00),
    ("instant 25k/5%", 25_000, 0.05, 250, 0.00),
]

def main():
    rows = []
    for name, nom, ml, fee, tgt in CASES:
        eff = nom * ml
        rows.append({
            "case": name, "nominal": nom, "max_loss_pct": ml,
            "effective_capital": eff,
            "illusion_ratio_nominal_over_effective": round(nom / eff, 1),
            "fee_usd": fee,
            "fee_as_pct_of_effective": round(fee / eff * 100, 2),
            "phase1_target_on_effective_pct": round(tgt / ml * 100, 1) if ml else 0.0,
        })
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e1_effective_capital.json").write_text(json.dumps(rows, indent=2))
    print("== E1 nominal vs effective capital ==")
    for r in rows:
        print(f"{r['case']:28s} eff=${r['effective_capital']:,.0f} "
              f"illusion x{r['illusion_ratio_nominal_over_effective']} "
              f"fee={r['fee_as_pct_of_effective']}%eff target={r['phase1_target_on_effective_pct']}%eff")
    print("\nHIDDEN PATTERN: headline size is marketing; compare fee/effective and target/effective.")
    return rows

if __name__ == "__main__":
    main()
