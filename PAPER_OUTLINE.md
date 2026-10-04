# Paper outline — from this benchmark to a publishable PhD paper
## Working title: *Gatekeeping by Drawdown: How Retail Funded-Trading Evaluations Measure Discipline Under the Guise of Capital Provision*

### Abstract (150 words, to be finalised after holdout 2027+)
Retail funded-trading evaluations sell large nominal accounts governed by small loss allowances. We formalise the *illusion ratio* (nominal/effective capital) and benchmark three archetypal programs (two-step/static, one-step/EOD-trailing, instant/tight-trailing) with a shared rule engine on 2018–2026 public equity/FX data plus calibrated Monte-Carlo. A breakeven trader reproduces the published 6–20% pass band; a modest edge doubles–triples it. Behaviour isolation (same signal, disciplined vs reckless execution) shows daily-limit clustering kills overtraders in 13–50 trades while disciplined twins survive 400–1,700 — yet without edge even discipline bleeds. Risk follows an inverted-U (0.25% dies of the clock, 2% of the daily limit). Best-day rules convert the sprint into a bi-objective problem. We publish the engine, data manifest, and control-group failures.

### IMRaD skeleton
1. **Introduction** — the two narratives (testimony vs statistics), research questions RQ1–RQ4 (measure? filter? shape behaviour? price fairly?).
2. **Related work** — prop-labour sociology (Ketmanee 2026), gate design (Hall 2026), fixed-size value (Youngblood 2026), validation methodology (Pardo; Bailey-LdP; Harvey; arXiv:2512.12924; DaruFinance harness).
3. **Methods** — archetype construction protocol (how help-centres were coded, inter-rater rule), engine semantics (static/EOD/intraday, daily ref, consistency, min-days), signal instruments (why SMA/ATR as behaviour isolator), cost ladder, Monte-Carlo design (seeds, n=2.5–3k paths, cost $15), live-data pipeline (Yahoo→Stooq→synthetic, SHA manifest), pre-registration (targets, gates, holdout 2027+).
4. **Results** — E1–E9 tables with CIs (add Wilson CIs for pass rates; bootstrap CIs for Sharpe — TODO), calibration plot (simulated vs published band), hazard decomposition (daily vs max competing risks), inverted-U with confidence bands.
5. **Discussion** — illusion-ratio pricing, trailing-as-fragility, two deaths, hero-day mechanism design, tuition EV and credit-risk ethics.
6. **Limitations** — §10 of README, verbatim + tick-data gap plan.
7. **Conclusion + reproducibility statement** — Docker image hash, data manifest hash, contract screenshots, code/data availability.

### Pre-registration (fill before running holdout)
- Primary outcome: phase-1 pass indicator per program archetype.
- Secondary: breach-type (daily/max), best-day share, Calmar, payout-reach (simulated funded stage with withdrawal rule).
- Fixed hyperparams: risk {0.5%, 0.75%, 1%}, costs {$12, $15, $20}, trades/day {2, 3}, disciplines {steady, reckless}.
- Holdout: 2027-01-01+ bars, untouched during development. Walk-forward: purged, embargo 5 days. Multiple-testing: DSR + PBO/CSCV gates (promote full `metrics.deflated_sharpe_lite` to Bailey-LdP exact + CSCV implementation).
- Decision rule: promote a signal only on majority-pass WFO + no catastrophic veto (drawdown-integrity break), per AlgoXpert-style gates.

### Per-chapter data shopping list
- Ch1: monthly panel of 30–50 firms' public terms (target, max/daily %, basis, trailing flavour, consistency, min-days, fee, split) — scrape + archive (Wayback snapshots).
- Ch2: any obtainable account-level panel (partner with journaling-tool vendor; else extend simulator with regime-switching DGP).
- Ch3: structural variation — firms that *changed* a rule (use CapitalCritic fine-print tracker events as natural experiments).
- Ch4: experience-sampling screen-time + trade-timestamp panel (pre-registered, IRB).
- Ch5: session-filtered signals on 1h bars (NQ, XAUUSD, EURUSD) with news blackout calendar (ForexFactory/ICS) + tick slippage model.

### Reviewer inoculation checklist
- [ ] Wilson CIs on every pass rate; bootstrap CIs on Sharpe/Calmar.
- [ ] Cost-ladder sensitivity (every headline number × {$0, $12, $15, $20}).
- [ ] Ablation: each rule removed singly (which rule does the filtering work?).
- [ ] Negative-result section kept (E8) — reviewers trust papers that show the control failing.
- [ ] No firm recommendation anywhere; archetype disclaimer on every figure.
- [ ] Ethics: gambling-risk paragraph + support signposting (kept from README §13).
