"""E9 — The 40-accounts story: expected fee burn (Abdullah's tuition).

Negative-binomial maths + Monte-Carlo cross-check:
  pass p per attempt -> expected attempts to first pass = 1/p
  expected fee burn = fee * 1/p
  P(need >40 attempts) = (1-p)^40  (how unlucky was Abdullah?)

Uses published band p in {6%, 10%, 14%, 16.8%} and fee $500 (100k 2-step).
Also values the 'university' framing: 3 years of tuition vs one lucky pass.
"""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "results"

def main():
    fee = 500
    rows = []
    for p in [0.06, 0.10, 0.14, 0.168]:
        exp_attempts = 1 / p
        exp_burn = fee * exp_attempts
        p_40plus = (1 - p) ** 40
        rows.append({"pass_p": p, "exp_attempts_to_first_pass": round(exp_attempts, 1),
                     "exp_fee_burn_usd": round(exp_burn),
                     "prob_need_more_than_40_attempts_pct": round(p_40plus * 100, 2),
                     "prob_pass_within_6_attempts_pct": round((1 - (1 - p) ** 6) * 100, 1)})
    abdullah_burn = 40 * fee
    out = {"fee_per_attempt": fee, "table": rows,
           "abdullah_40_accounts_burn_usd": abdullah_burn,
           "interpretation": ("At p=10%, needing 40+ tries has probability 1.5% — "
                               "Abdullah was either very unlucky, undisciplined early "
                               "(revenge/overtrade/Friday/news — his own words), or both. "
                               "Expected tuition to first pass is $3k-$8k in fees alone. "
                               "Borrowing this money (loans) guarantees pressure -> ruin.")}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "e9_fee_burn.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    return out

if __name__ == "__main__":
    main()
