# From Nominal to Effective: A Reproducible Benchmark of Retail Funded-Trading Accounts
## Verifying practitioner claims (two-step discipline, trailing-drawdown traps, overtrading disease) against live market data, 2018–2026

**Status: working research benchmark — not financial advice. No live capital was risked. All results re-runnable with one command.**

> **One-line summary.** A `$100,000` funded account with a 10% maximum loss is a `$10,000` risk account wearing a `$100,000` costume (E1). Under identical order flow, a static floor survives pullbacks that kill an intraday-trailing twin (E2). A personal daily stop at half the firm's limit cuts simulated breach rates by ~41% (E3). On 2018–2026 Yahoo data (SPY/QQQ/GLD/EURUSD, n≈2,200 bars each), the same SMA/ATR toy run disciplined (1 trade/day, 0.5%, no Fridays) survives 400–1,700 trades while its reckless twin (5 trades/day, 2%, revenge sizing) dies in 13–50 trades — yet discipline alone does not manufacture edge (E4/E8: a no-edge toy still bleeds). Monte-Carlo calibration reproduces the published 2025–26 industry pass band (6–20%) from a *breakeven* trader and shows a genuine edge roughly doubling–tripling pass rates — the rules are a skill filter, not a lottery (E5). Risk-per-trade follows an inverted-U: 0.25% dies of the clock, 2% dies of the daily limit, ~0.75–1.0% maximises pass probability for an 8% target (E6). A +6% month concentrated in one hero day fails the 50% best-day rule while the same +6% spread over six days passes (E7). At a 10% per-attempt pass rate, the expected tuition to the first pass is ~$5,000 in fees; needing 40+ attempts has probability ~1.5% — consistent with an undisciplined early phase, in the narrator's own words (E9).

---

## Table of contents
1. [Why this benchmark exists](#1-why-this-benchmark-exists)
2. [Practitioner claims under test (H1–H9)](#2-practitioner-claims-under-test-h1h9)
3. [Literature & industry base rates (2025–2026)](#3-literature--industry-base-rates-20252026)
4. [Zero-to-hero verification protocol](#4-zero-to-hero-verification-protocol)
5. [Repository map](#5-repository-map)
6. [Data provenance (live, public, hashed)](#6-data-provenance-live-public-hashed)
7. [The rule engine (what is actually simulated)](#7-the-rule-engine-what-is-actually-simulated)
8. [Results E1–E9 (all reproduced 2026-10-04)](#8-results-e1e9-all-reproduced-2026-10-04)
9. [Hidden patterns (the PhD-relevant findings)](#9-hidden-patterns-the-phd-relevant-findings)
10. [Threats to validity (read before citing)](#10-threats-to-validity-read-before-citing)
11. [From benchmark to PhD paper (concrete roadmap)](#11-from-benchmark-to-phd-paper-concrete-roadmap)
12. [Reproduce everything](#12-reproduce-everything)
13. [Ethics & risk disclaimer](#13-ethics--risk-disclaimer)
14. [References](#14-references)
15. [Citation](#15-citation)

---

## 1. Why this benchmark exists

Retail funded-trading ("prop firm challenges") is where two narratives collide:

- **Practitioner narrative (Arabic trading podcasts, 2025–26):** a funded trader describes blowing *40+ accounts in one year*, 12-hour chart-staring (10:00–22:00), revenge trading, and eventual survival through two-step discipline, 0.5%-style sizing, quitting Fridays, and treating trading as a multi-year university rather than a lottery ticket. A second educator video dissects the mechanics: nominal-vs-effective capital, static-vs-trailing drawdown, daily-loss micro-breaches, payout≠passing, banned strategies, and a buyer checklist.
- **Industry statistics (2025–26):** pass rates of ~6–20% per attempt, ~7% of buyers ever paid, average payout ~4% of nominal (see §3).

Both narratives are *testable*. This repo turns nine of their claims into executable experiments with public data, a documented rule engine, and Monte-Carlo calibration — so that a future PhD chapter (or a sceptical beginner) can check every number instead of trusting screenshots.

**Deliberate scope limit.** We do **not** recommend any firm, sell signals, or promise income. We model *archetypal* programs (2-step/static, 1-step/EOD-trailing, instant/tight-trailing) distilled from public help-centres — never a single firm's live terms, which change without notice.

---

## 2. Practitioner claims under test (H1–H9)

| ID | Claim (paraphrased from the two videos) | Experiment | Verdict (this data) |
|----|------------------------------------------|------------|---------------------|
| H1 | "The $100k is not yours; your real capital is the allowed loss." | E1 effective-capital arithmetic | **Confirmed arithmetically.** 10% max ⇒ $10k effective (illusion ×10); 5% ⇒ ×20. Fee/target must be quoted on effective. |
| H2 | "Two-step teaches discipline; instant bonuses are a trap." | E2 trailing-trap + E5 model comparison | **Confirmed directionally.** Same path: static survives, intraday-trailing breaches. Breakeven pass: 2-step 17.6% > instant 15.7% > 1-step 7.4%. |
| H3 | "12-hour chart-staring (chart–prayer–chart) destroys you." | E4 overtrading on live data | **Confirmed as mechanism.** Reckless dies in 13–50 trades (daily-limit cluster); disciplined survives 400–1,700. But discipline ≠ edge (see H8). |
| H4 | "Blowing 40 accounts is the tuition; then discipline clicks." | E9 fee-burn + E5 base rates | **Plausible, quantified.** At p=10%, E[attempts]=10, E[burn]=$5k; P(40+)=1.48%. 40 implies early-phase indiscipline (his own account) or deep tail bad luck. |
| H5 | "Risk 0.5–1%, personal stop inside the firm's stop." | E3 daily-stop + E6 risk sweep | **Confirmed with shape.** Personal 2.5% vs firm 5% ⇒ −40.9% breaches. Inverted-U peaks ~0.75–1.0% for an 8% target. |
| H6 | "Passing the target ≠ getting paid (consistency rule)." | E7 best-day rule | **Confirmed mechanically.** +6% via one hero day (83% share) FAILS 50% rule; same +6% over 6 days PASSES. |
| H7 | "Keep the job; quit only at 2× salary for 6–8 months." | E8 variance + E9 EV | **Supported by arithmetic.** Monthly payouts are high-variance; fee EV is negative without edge. No experiment can certify a resignation rule — we quantify the variance that motivates it. |
| H8 | "Strategy + money-management + discipline, all three." | E8 live backtest matrix | **Confirmed as conjunction.** Toy SMA/ATR (no edge, PF 0.81–1.0, Sharpe ≤0.04) bleeds even when disciplined. Discipline extends life; only edge pays. |
| H9 | "One screen is enough; stacks of monitors are décor." | Design note (not simulated) | **Out of scope for backtest.** Recorded as qualitative claim; a future HCI/screen-time study could test it (see §11). |

---

## 3. Literature & industry base rates (2025–2026)

All figures below are *firm-reported or vendor-reported, unaudited* — cited so the reader can anchor our calibration, not as ground truth.

- **FPFX Tech dataset via Finance Magnates (300k+ accounts, 100k traders, 10 firms):** ~14% pass, ~7% of all buyers ever paid, average payout ~4% of nominal, average spend ~$800 across ~3 attempts.
- **Topstep 2025 disclosure:** 16.8% of Combines passed; 51.8% of *persons* ever funded (median ~6 attempts per pass); 33.3% of funded paid; 0.71% reached live. First-day blow-up ~63%.
- **Tradeify (Aug 2025–Jul 2026):** 17.2% evaluations passed; 28.5% of funded paid.
- **MyFundedFutures:** ~19.97% advanced; ~39.2% of funded paid.
- **HyroTrader live dashboard (Sep 2026):** 13.49% 1-step / 8.70% 2-step.
- **ATFunded Jun 2025:** 22.6% P1→P2 × 26.9% P2→funded ≈ 6% overall.
- **Academic 2026:** Youngblood (SSRN 7514219) on fixed-size strategy value under prop constraints; Ketmanee (Kasetsart J. 2026) sociology-of-finance critique of evaluation labour; Andriushchenko et al. (2026) polynomial-regime models noting buy-and-hold beat intraday automation in 6-month live tests; Hall (SSRN 7453580) on gate design and stage-dependent incentives; DaruFinance (2026) walk-forward + DSR/PBO robustness harness; arXiv:2512.12924 walk-forward validation framework (34 folds, honest null reporting, p=0.34).

**Methodology debt we repay:** Bailey & López de Prado (2014) DSR/PBO; Pardo (1992/2008) walk-forward; Harvey et al. (2016) multiple-testing haircuts; Freqtrade docs (lookahead-analysis, backtesting assumptions) for no-lookahead enforcement.

---

## 4. Zero-to-hero verification protocol

Every file in this repo was held to the following contract (synthesised from the 2026 best-practice search: DaruFinance parity harness, Freqtrade lookahead checks, arXiv WFV discipline):

1. **One web-search at a time; every factual rule grounded in a retrievable source** (§3–§14). No invented firm terms.
2. **No lookahead, ever.** Signals shift by one bar (`strategies.add_features`); `tests/test_no_lookahead.py` proves signal[t] = f(data ≤ t−1); ATR uses trailing 14 bars only.
3. **Costs inside the breach check.** Spread+commission deducted *before* daily/max-loss evaluation (firms count them — Mo'men secret #3).
4. **Equity-basis strictness.** Floating P&L counts toward breach (harshest, most conservative).
5. **Live-first data.** `data_loader` tries Yahoo → Stooq → seeded-synthetic, caches to `data/*.csv`, and writes `data/MANIFEST.txt` with row counts, dates, source labels, and SHA-16 hashes.
6. **Calibration before storytelling.** Monte-Carlo must reproduce the 6–20% industry band from a breakeven trader *before* any "strategy works" claim (E5 does; E8 honestly reports a negative result).
7. **Every number re-runnable.** `make all` / `docker compose run research` regenerates `results/e1…e9.json`; `pytest` gates the rule engine. If it doesn't run, it doesn't ship.

---

## 5. Repository map

```
config/funded_programs.yml      # 3 archetypal programs (NOT live firm terms)
src/
  data_loader.py                # yahoo -> stooq -> synthetic, cached + hashed
  funded_rules.py               # static / trailing-EOD / trailing-intraday + daily + consistency + min-days
  strategies.py                 # disciplined vs reckless (SAME signal, different behaviour)
  backtest.py                   # event-driven daily engine under the rule wrapper
  montecarlo.py                 # challenge simulator reusing the SAME FundedAccount class
  metrics.py                    # Sharpe/Sortino/Calmar + DSR-lite (labelled lite on purpose)
  experiments/
    e1_effective_capital.py ... e9_fee_burn.py
    run_all.py                  # end-to-end + results/SUMMARY.md
tests/
  test_funded_rules.py          # 6 rule-engine tests (static/trailing/daily/consistency/effective)
  test_no_lookahead.py          # 3 lookahead/data-integrity tests
Dockerfile + docker-compose.yml # one-command reproduce (research + test services)
Makefile                        # make test | make e1..e9 | make all | make docker-run
results/                        # generated JSON (git-ignored except .gitkeep)
data/                           # cached CSVs + MANIFEST.txt (git-ignored except .gitkeep)
PAPER_OUTLINE.md                # the publishable-paper skeleton (IMRaD + pre-registration)
```

---

## 6. Data provenance (live, public, hashed)

Run of 2026-10-04 (UTC) downloaded **live Yahoo Finance** bars (no key, fully public):

| Symbol | Proxy for | Rows | Span | Source | SHA-16 |
|--------|-----------|------|------|--------|--------|
| SPY | S&P 500 / US500 | 2,200 | 2018-01-02 → 2026-10-02 | yahoo | a0d698ddc9604211 |
| QQQ | Nasdaq-100 / NAS100 | 2,200 | 2018-01-02 → 2026-10-02 | yahoo | 0e12b33c9588a8f0 |
| GLD | Gold / XAUUSD | 2,200 | 2018-01-02 → 2026-10-02 | yahoo | fb2c81b6515e14ff |
| EURUSD | EURUSD=X FX | 2,279 | 2018-01-01 → 2026-10-02 | yahoo | eea8c3f6ef58f41a |

Full manifest: `data/MANIFEST.txt` (regenerated each run). Re-run offline falls back to Stooq, then to labelled seeded-synthetic — never silently.

---

## 7. The rule engine (what is actually simulated)

`FundedAccount` implements the firms' own mechanics as documented in §3:

- **Static floor:** `nominal × (1 − max%)`, never moves (FTMO-like 10% ⇒ $90,000 on $100k).
- **Trailing-EOD floor:** `peak_close − max_loss`, ratchets on *closes only*, **freezes at breakeven** once `peak ≥ nominal + max_loss` (Topstep/Apex-style lock; real Apex uses start+$100 — documented $100 variant in code comments).
- **Trailing-intraday floor:** ratchets on *equity highs including open P&L* — a wick you never bank still raises your floor.
- **Daily loss:** `ref = max(prev_balance, prev_equity)`; breach if `equity ≤ ref × (1 − daily%)`. Server-day reset semantics; costs counted.
- **Consistency (best-day):** `best_day / total_profit ≤ cap` (50% eval / 40% instant archetypes), else target is *not* passed — you must keep trading.
- **Min trading days:** evaluation needs N distinct traded days.
- **Effective capital:** `nominal × max%` (Mo'men's core ratio); illusion ratio = nominal/effective.

Trade PnL (transparent by design): `R = direction × (close − open) / ATR_trailing14`, `pnl = clip(R, −1, +1.5R) × risk_usd − cost`. Same signal (SMA20 trend, shifted one day) for both behaviours — the *only* difference is risk/frequency/discipline.

---

## 8. Results E1–E9 (all reproduced 2026-10-04)

### E1 — Nominal vs effective (the costume comes off)

| Case | Effective | Illusion | Fee/effective | Phase-1 target on effective |
|------|-----------|----------|---------------|-----------------------------|
| 2-step $100k/10% | $10,000 | ×10 | 5.0% | 80% |
| 2-step $25k/10% | $2,500 | ×10 | 6.0% | 80% |
| 1-step $100k/6% | $6,000 | ×16.7 | 10.0% | 166.7% |
| Instant $100k/5% | $5,000 | ×20 | 18.0% | — (no target, tighter leash instead) |

**Read it as:** an 8%-nominal target is an **80%-on-risk-capital** sprint; a $500 fee is **5% of risk capital per attempt**. Never compare headline sizes — compare fee/effective and target/effective.

### E2 — The trailing trap (same path, three fates)

Path `100k → 105k → 96k pullback → 102k` (plus a 107k intraday wick variant):

| Floor | End floor | Fate of the 96k pullback |
|-------|-----------|--------------------------|
| Static 10% | $90,000 | **Survives** ($6k buffer) |
| Trailing-EOD 10% | $95,000 | Survives barely ($1k buffer) |
| Trailing-intraday 10% (107k wick) | $97,000 | **BREACHED** at $96,000 |

**Read it as:** profit *raises* the floor under trailing. Abdullah's "take the two-step" is mechanically sound advice for learners: static/EOD forgives; intraday punishes wicks.

### E3 — The personal stop (firm limit is the cliff, not the plan)

Firm 5% daily, trader risking 1%/trade × 4 trades/day, 20 days, p=0.45/RR=1.5:

| Policy | Breach rate (n=3,000) |
|--------|----------------------|
| Stop at the firm limit (5%) | 88.3% |
| Personal stop at 2.5% (walk away) | 52.2% (**−40.9% relative**) |

**Read it as:** the 50–60% personal-stop rule found across 2026 risk guides is not folklore; it mechanically removes the slippage/revenge tail.

### E4 — Screen-time disease on live data (same signal, two behaviours)

2-step/static $100k, disciplined (1/day, 0.5%, no Friday, half-limit stop) vs reckless (5/day, 2%, revenge ×2, Fridays), SMA20/ATR toy, $12/trade:

| Symbol | Disciplined | Reckless |
|--------|-------------|----------|
| SPY | $89,966, max-loss breach, n=950 | daily breach, n=50 |
| QQQ | **$100,551, alive**, n=1,743 | daily breach, n=13 |
| GLD | $89,545, max-loss breach, n=424 | daily breach, n=50 |
| EURUSD | max-loss breach, n=773 | max-loss breach, n=613 |

**Honest reading (negative-result discipline):** the toy has no edge (it shorts bull trends), so most legs die *either way* — discipline changes *how* you die (slow 400–1,700-trade bleed vs 13–50-trade daily execution) and salvages QQQ. Discipline is **necessary but not sufficient**; edge + costs still decide (see E8).

### E5 — Model comparison, calibrated (the skill filter)

Same trader, 3 trades/day, ≤60 trades, $15/trade costs:

| Trader | 2-step/static | 1-step/EOD-trailing | Instant/tight-trailing |
|--------|---------------|---------------------|------------------------|
| **Population breakeven** (p=0.40, RR=1.5, EV≈0 pre-cost) | **17.6%** | **7.4%** | **15.7%** |
| Skilled (p=0.45, RR=1.5, EV>0) | 43.9% | 23.4% | 34.7% |

**Read it as:** the breakeven row reproduces the published 2025–26 band (Topstep 16.8%, FPFX 14%, Hyro 13.5%/8.7%) — the engine is calibrated. A real edge roughly doubles–triples pass rates. Ordering static > instant > 1-step holds for both skill levels. Daily-limit deaths dominate the tighter (3%) programs (40–55% daily-breach) while the 5%-daily 2-step dies by max-loss instead — exactly Mo'men's "daily trap" asymmetry.

### E6 — Risk sweep: the inverted-U (population trader, p=0.42/RR=1.5)

| Risk/trade | Pass | Daily-breach | Max-breach | Cause of death |
|------------|------|--------------|------------|----------------|
| 0.25% | 0.0% | 0.0% | 0.0% | **The clock** — cannot reach 8% in 60 trades |
| 0.50% | 4.8% | 0.0% | 1.8% | Too slow |
| 0.75% | 20.2% | 0.0% | 10.7% | Sweet spot |
| 1.00% | **27.4%** | 0.0% | 20.0% | Sweet spot (upper) |
| 2.00% | 7.3% | **91.3%** | 1.4% | **The daily limit** |

**Read it as:** the textbook table ("5 losses to death at 1%, 2 at 2%") with the missing half restored — *too little* risk also fails, via the target clock. Size for the target *and* the leash.

### E7 — Consistency: hero vs grind (both finish +6%)

| Path | Best-day share | 50% rule |
|------|---------------|----------|
| Hero: +5%, +0.5%, +0.5% | 83.3% | **FAIL** — keep trading |
| Grind: +1% × 6 days | 16.7% | **PASS** |

**Read it as:** Mo'men's "passing ≠ paid" in one table. Size for repeatability, not screenshots.

### E8 — Full live-data matrix (the reality check the industry won't show you)

Disciplined toy on 2018–2026 data, 2-step/static:

| Symbol | End | P&L | Trades | Win% | PF | Sharpe | MaxDD | 8% hit? |
|--------|-----|-----|--------|------|----|--------|-------|---------|
| SPY | $89,966 | −10.0% | 950 | 46.8% | 0.92 | −0.48 | 10.9% | No (breached) |
| QQQ | $100,551 | +0.6% | 1,743 | 49.3% | 1.00 | +0.04 | 8.1% | No (alive, target missed) |
| GLD | $89,545 | −10.5% | 424 | 45.3% | 0.81 | −1.17 | 13.3% | No (breached) |
| EURUSD | $89,994 | −10.0% | 773 | 16.6% | 0.11 | −11.2 | 10.0% | No (breached) |

**Read it as:** a published-style *negative result*. A naive trend toy (PF ≤ 1.0 everywhere) cannot clear an 8% phase — which is precisely why population pass rates sit at 6–20% and why "buy → blow → rebuy" is the modal loop. Anyone selling a toy like this as a pass-guarantee is selling the loop.

### E9 — The 40-account tuition (negative-binomial EV)

Fee $500/attempt (archetypal $100k 2-step):

| True pass p | E[attempts] | E[burn] | P(need >40) | P(pass within 6) |
|-------------|-------------|---------|-------------|------------------|
| 6% | 16.7 | $8,333 | 8.42% | 31.0% |
| 10% | 10.0 | $5,000 | **1.48%** | 46.9% |
| 14% | 7.1 | $3,571 | 0.24% | 59.5% |
| 16.8% | 6.0 | $2,976 | 0.06% | 66.8% |

Abdullah's 40 × ~$500 ≈ **~$20,000** in fees. At p=10%, needing 40+ is a 1.5% tail — i.e. either brutal bad luck or (his own testimony) an early undisciplined phase of revenge/overtrade/Friday/news trading. Either way: **never borrow this tuition** (loans convert variance into ruin-pressure).

---

## 9. Hidden patterns (the PhD-relevant findings)

1. **The illusion ratio is the right unit of account.** Headline size explains nothing; `fee/effective` and `target/effective` explain everything (E1). A $25k/10% account can dominate a $100k/5% account on both ratios — the market prices headlines, survivors price ratios.
2. **Trailing converts profit into fragility.** The floor is a ratchet, not a buffer (E2). Optimal policy under trailing is *counter-intuitive*: trade smaller after wins until the breakeven lock, the opposite of Kelly-style compounding.
3. **Two distinct deaths.** Disciplined accounts die by the *max-loss clock* (slow bleed); reckless accounts die by the *daily guillotine* (fast cluster) (E3–E5). Any survival analysis that pools them misestimates both hazards — a directly testable thesis chapter.
4. **The inverted-U of risk (E6).** The literature documents the right tail (over-risk ⇒ breach) but rarely the left tail (under-risk ⇒ clock-death). Our sweep shows both: 0.25% passes 0%, 1% passes 27%, 2% passes 7%.
5. **Consistency as a second target (E7).** The best-day rule turns a single-objective sprint into a bi-objective problem (hit X% *with* max-day ≤ c%). Hero-day strategies are inadmissible — a clean mechanism-design chapter.
6. **Calibration as proof of skill-filtering (E5).** Reproducing 6–20% from breakeven play *plus* 2–3× lift from a modest edge is stronger evidence than any single backtest that "the firms sell discipline measurement, not capital."
7. **Negative-result honesty (E8).** A transparent no-edge toy fails on live data with full audit — the control group most marketing backtests omit.

---

## 10. Threats to validity (read before citing)

- **Archetypes, not firms.** Programs are distilled composites; live terms (spreads, swaps, news blackouts, payout delays, KYC, server-day definitions) differ per firm *and change*. Re-check before buying anything.
- **Daily-bar granularity.** Intraday wicks, news spikes, slippage bursts, and weekend gaps are approximated (intraday trailing is modelled; tick-level latency arb is not). Futures/CFD tick replication is future work.
- **Toy signal.** SMA20/ATR is a behaviour-isolating instrument, not a proposed edge. Real edges (liquidity sweeps, daily bias, session filters) need tick/session data and news calendars.
- **Cost assumptions.** $12–$15/trade + spread proxy is explicit and swept nowhere near enough — costs decide more challenges than entries. Treat our absolute pass levels as *conditional on costs*.
- **Monte-Carlo distributional risk.** Fixed (p, RR) iid draws ignore autocorrelation, regime shifts, and revenge-driven distribution change (we model revenge sizing in E4, not in E5/E6 draws).
- **Survivorship/reporting bias in anchors.** All industry base rates are firm- or vendor-reported and unaudited. Our calibration inherits that uncertainty.
- **No out-of-sample holdout split shown.** The 2018–2026 window is one history. A thesis must add purged walk-forward + DSR/PBO (scaffolded in `metrics.deflated_sharpe_lite`, full CPCV in §11).

---

## 11. From benchmark to PhD paper (concrete roadmap)

**Candidate title:** *Gatekeeping by Drawdown: How Retail Funded-Trading Evaluations Measure Discipline Under the Guise of Capital Provision.*

1. **Chapter 1 — Measurement.** Formalise (nominal, effective, illusion ratio, fee/effective, target/effective) and test H1 across 50 firms' public terms (scraped panel, monthly).
2. **Chapter 2 — Hazard decomposition.** Competing-risks survival model (daily vs max-loss vs consistency-censoring) on the E4/E5 simulator validated against any obtainable account-level panel; predicts the "two deaths" pattern (§9.3).
3. **Chapter 3 — Mechanism design.** Best-day/min-days/news-window rules as effort-shaping contracts; structural estimation of how much each rule depresses hero-day strategies (E7 → structural).
4. **Chapter 4 — Behavioural panel.** Screen-time/trade-frequency causality: instrument overtrading with payout-rule tightness; test Abdullah's 12-hour claim with timestamped journals (experience-sampling, pre-registered).
5. **Chapter 5 — Live validation.** Purged walk-forward + CPCV + DSR on session-filtered liquidity/bias signals with full cost ladder; pre-registered holdout 2027+; negative-result reporting per arXiv:2512.12924.
6. **Novelty statement.** First open benchmark that (i) unifies Arabic practitioner testimony with industry base rates, (ii) calibrates simulation to published pass bands, (iii) isolates behaviour from signal on live data, and (iv) publishes the control-group failure.

See `PAPER_OUTLINE.md` for the IMRaD skeleton, pre-registration fields, and per-chapter data requirements.

---

## 12. Reproduce everything

```bash
# fastest (uses cached data if present, downloads live Yahoo otherwise)
pip install -r requirements.txt
make test          # 9 rule-engine + lookahead tests
make all           # all 9 experiments -> results/*.json + results/SUMMARY.md

# single experiments
make e1   # effective capital      make e5   # model comparison (calibration)
make e2   # trailing trap          make e6   # risk inverted-U
make e3   # personal daily stop    make e7   # consistency hero-vs-grind
make e4   # overtrading, live data make e8   # full live matrix
                               make e9   # 40-account tuition EV

# docker (bit-identical env)
docker compose build
docker compose run --rm test       # pytest inside container
docker compose run --rm research   # full benchmark inside container
```

Outputs: `results/e1_effective_capital.json` … `results/e9_fee_burn.json`, `results/summary.json`, `results/SUMMARY.md`, `data/MANIFEST.txt`.

---

## 13. Ethics & risk disclaimer

- This is **research software and education**, not investment advice, not a recommendation to buy any challenge, and not a signal service.
- Trading (funded or personal) can lose more than fees/deposits; most buyers lose (see §3 base rates). Never trade borrowed money; never risk essentials (the videos' own warning, quantified in E9).
- Authors have no affiliation with any firm named; firm names appear as factual anchors for public statistics only.
- If you are experiencing gambling-like symptoms (chasing, borrowing, sleeplessness — described frankly in the testimony), pause trading and seek local professional support.

---

## 14. References

**Industry statistics & rule mechanics (retrieved Oct 2026; firm-reported, unaudited):**
- ThePropJournalist — *Prop Firm Pass Rates 2026: Official Data From 50 Firms* (Topstep 16.8%, Tradeify 17.2%, MFF 19.97%, FunderPro 7.35%, first-day blow-ups). https://thepropjournalist.com/analysis/prop-firm-pass-rates/
- ITAfx Blog — *Prop Trading Industry Statistics 2026* (FPFX 300k-account dataset: 14% pass, 7% ever paid, avg payout 4%). https://www.itafx.com/blog/prop-trading-industry-statistics-2026/
- PropDataLab — *Prop Firm Pass Rates: Only 4 of 10 Firms Publish One* (attempt-vs-person denominators). https://propdatalab.com/prop-firm-pass-rates/
- HyroTrader Blog — *Prop Firm Pass Rates: Live Numbers 2026* (13.49% 1-step / 8.70% 2-step dashboard). https://www.hyrotrader.com/blog/prop-firm-pass-rates/
- CapitalCritic — *1% Rule for Funded Traders* (5-losses-to-daily at 1%); *Prop Firm Rule Changes 2026 tracker* (Topstep consistency 50→55%, E8 price moves). https://www.capitalcritic.ai/blog/risk-management-funded-traders-1-percent-rule
- The5ers Academy — *Drawdown Rules Explained: Daily vs Max (2026)*; BrokerChampion — *Drawdown Rules Explained (2026): Static vs Trailing*; PropJournalist — *Drawdown Rules: Ultimate Guide*; PFMatrix — *Static vs Trailing*; PropNavi — *Trailing vs Static* (intraday vs EOD, balance vs equity, lock-at-breakeven mechanics).
- TradeThePool — *Prop Firm Risk Rules* (daily pause vs max termination, 30–50% consistency caps); Bucko.ai — *Consistency Rule* & *Daily Loss Limit* explainers; OneFunded — *Risk Management Framework* (0.5%/trade, 3-open cap, 1.5% personal stop; 78.7% fail on daily).
- PropJournal — *Risk Management for Funded Accounts (2026)* (60% daily-budget rule, −30–50% sizing on funded vs eval).

**Validation methodology (the zero-to-hero protocol):**
- Bailey, D. & López de Prado, M. (2014). Pseudo-mathematics and financial charlatanism (DSR). *Notices AMS*.
- López de Prado, M. (2018). *Advances in Financial Machine Learning* (CPCV/PBO). Wiley.
- Pardo, R. (1992/2008). *Design, Testing, and Optimization of Trading Systems* (walk-forward).
- Harvey et al. (2016). …and the Cross-Section of Expected Returns (multiple-testing haircuts).
- arXiv:2512.12924 (2025). *A Rigorous Walk-Forward Validation Framework* (34-fold, honest nulls).
- DaruFinance (2026). *quant-research-framework* (WFO + DSR/PSR/PBO + Rust parity harness). https://github.com/DaruFinance/quant-research-framework
- Freqtrade docs (2026). *Backtesting assumptions; Lookahead-analysis; Strategy-101* (no-lookahead enforcement pattern).
- TradeQuant/IRJMETS (2025). Per-instrument cost modelling; timeframe-dependent cost impact (M1 −$12.7k vs H4 +$22.3k same logic).

**Academic 2026 on prop evaluations:**
- Youngblood, Z. (2026). *Inherent Value of Retail Prop Firms for Fixed-Size Strategies.* SSRN 7514219.
- Ketmanee, T. (2026). *Becoming digital labor on forex prop platforms.* Kasetsart J. Soc. Sci. 47(3).
- Andriushchenko et al. (2026). *Polynomial models for prop-trader algos.* (live buy-and-hold beat automation).
- Hall, N. (2026). *Gate Design and Stage-Dependent Incentives in Retail Prop Evaluations.* SSRN 7453580.

**Primary practitioner sources (testimony under test):**
- Arabic podcast testimony (Abdullah): 40+ blown accounts, 10:00–22:00 screen disease, 2-step preference, job-plus-trading doctrine, signals-loss anecdote (~10–20k AED), multi-screen myth, résumé of §2 H-claims.
- Mo'men Medhat educator video: funded=demo+bonus mechanics, 2-step/1-step/instant taxonomy, fee-pool business model, five secrets (effective capital, trailing types, daily trap, payout≠pass, banned strategies), buyer checklist.

---

## 15. Citation

```bibtex
@software{funded_accounts_truth_benchmark_2026,
  title  = {From Nominal to Effective: A Reproducible Benchmark of Retail Funded-Trading Accounts},
  year   = {2026},
  note   = {9 experiments, live Yahoo/Stooq data with SHA manifest, Docker-reproducible. Not financial advice.},
  url    = {file:// /home/md/src/funded-accounts-truth-benchmark-2026}
}
```

*Research use only. Re-run before you cite: numbers regenerate from live data (`make all`), and firms change terms without notice — always verify against the firm's current help-centre and keep a screenshot of the contract you sign (Mo'men's checklist, itemised in E5/E7 configs).*
