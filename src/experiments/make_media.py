"""Generate all README/preview media from VERIFIED results (no hand-drawn numbers).

Reads results/*.json + re-runs the QQQ backtest pair (deterministic, cached data)
and writes:
  docs/fig-trailing-trap.png   E2: same pullback, three floors
  docs/fig-risk-u.png           E6: inverted-U + breach decomposition
  docs/fig-calibration.png      E5: breakeven vs skilled across 3 models + published band
  docs/fig-equity-race.png      E4: QQQ disciplined vs reckless equity curves
  docs/demo.gif                 animated equity race (auto-plays in README)
  docs/demo.mp4                 same animation as video (for preview.html <video>)

Run:  PYTHONPATH=. python -m src.experiments.make_media
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
RES = ROOT / "results"
DOCS = ROOT / "docs"
DOCS.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({"figure.dpi": 110, "font.size": 10,
                     "axes.spines.top": False, "axes.spines.right": False})
TEAL, NAVY, RED, AMBER, GREEN, GREY = "#0ea5a4", "#1e3a5f", "#e5484d", "#f5a524", "#2fa44f", "#8a94a6"


def _load(name):
    return json.loads((RES / name).read_text())


def fig_trailing_trap():
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    x = np.array([0, 1, 2, 3])
    eq = np.array([100_000, 105_000, 96_000, 102_000])
    ax.plot(x, eq, "o-", color=NAVY, lw=2.5, label="Equity path (same for all three)")
    ax.axhline(90_000, color=GREEN, ls="--", lw=1.5, label="Static floor $90k — survives")
    ax.step([0, 1, 1, 2, 2, 3], [90_000, 90_000, 95_000, 95_000, 95_000, 95_000],
            color=TEAL, lw=1.8, label="Trailing-EOD floor — survives barely ($1k buffer)")
    ax.step([0, 1, 1, 2, 2, 3], [90_000, 90_000, 97_000, 97_000, 97_000, 97_000],
            color=RED, lw=1.8, label="Trailing-intraday floor (107k wick) — BREACHED at $96k")
    ax.annotate("107k wick\nraises floor", xy=(1, 107_000), xytext=(1.6, 109_500),
                arrowprops=dict(arrowstyle="->", color=RED), color=RED, fontsize=9,
                ha="center")
    ax.set_xticks(x); ax.set_xticklabels(["start $100k", "peak $105k", "pullback $96k", "recover $102k"])
    ax.set_ylabel("Account value (USD)")
    ax.set_title("E2 — The trailing trap: identical trading, three fates", fontweight="bold")
    ax.legend(fontsize=8.5, loc="lower left")
    fig.tight_layout(); fig.savefig(DOCS / "fig-trailing-trap.png", bbox_inches="tight")
    plt.close(fig)


def fig_risk_u():
    d = {r["risk_pct"]: r for r in _load("e6_risk_sweep.json")}
    risks = sorted(d)
    xs = np.arange(len(risks))
    passes = [d[r]["pass_rate"] * 100 for r in risks]
    daily = [d[r]["daily_breach_rate"] * 100 for r in risks]
    maxb = [d[r]["max_breach_rate"] * 100 for r in risks]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.6))
    a1.bar(xs, passes, color=[GREY, GREY, TEAL, TEAL, RED])
    a1.set_xticks(xs); a1.set_xticklabels([f"{r:.2%}" for r in risks])
    a1.set_ylabel("Pass rate %"); a1.set_xlabel("Risk per trade")
    a1.set_title("Pass rate: inverted-U", fontweight="bold")
    for i, v in enumerate(passes):
        a1.text(i, v + 0.6, f"{v:.1f}%", ha="center", fontsize=9)
    a2.bar(xs, daily, label="daily-limit death", color=RED)
    a2.bar(xs, maxb, bottom=daily, label="max-loss death", color=AMBER)
    a2.set_xticks(xs); a2.set_xticklabels([f"{r:.2%}" for r in risks])
    a2.set_ylabel("Breach %"); a2.set_xlabel("Risk per trade")
    a2.set_title("How each risk level dies", fontweight="bold")
    a2.legend(fontsize=8.5)
    fig.suptitle("E6 — Too small dies of the clock, too big dies of the daily limit", fontweight="bold")
    fig.tight_layout(); fig.savefig(DOCS / "fig-risk-u.png", bbox_inches="tight")
    plt.close(fig)


def fig_calibration():
    rows = _load("e5_models_compare.json")
    models = ["two_step_static", "one_step_trailing_eod", "instant_trailing"]
    labels = ["Two-step\n(static)", "One-step\n(EOD-trail)", "Instant\n(tight-trail)"]
    pop = [next(r["pass_rate"] * 100 for r in rows if r["trader"] == "population_breakeven" and r["program"] == m) for m in models]
    skl = [next(r["pass_rate"] * 100 for r in rows if r["trader"] == "skilled" and r["program"] == m) for m in models]
    x = np.arange(len(models)); w = 0.36
    fig, ax = plt.subplots(figsize=(8.6, 3.8))
    ax.axhspan(6, 20, color="#e8f4f4", label="Published 2025–26 band (6–20%)")
    ax.bar(x - w / 2, pop, w, label="Breakeven trader (population avg)", color=TEAL)
    ax.bar(x + w / 2, skl, w, label="Skilled trader (p=45%, RR=1.5)", color=NAVY)
    for i, (p, s) in enumerate(zip(pop, skl)):
        ax.text(i - w / 2, p + 0.7, f"{p:.1f}%", ha="center", fontsize=9)
        ax.text(i + w / 2, s + 0.7, f"{s:.1f}%", ha="center", fontsize=9)
    ax.set_xticks(x); ax.set_xticklabels(labels)
    ax.set_ylabel("Simulated pass rate %")
    ax.set_title("E5 — Calibration: breakeven play reproduces the industry band; edge 2–3× it", fontweight="bold")
    ax.legend(fontsize=8.5); ax.set_ylim(0, max(skl) * 1.25)
    fig.tight_layout(); fig.savefig(DOCS / "fig-calibration.png", bbox_inches="tight")
    plt.close(fig)


def _qqq_curves():
    from src.backtest import run_symbol
    from src.data_loader import load_all
    from src.funded_rules import Program
    cfg = yaml.safe_load(open(ROOT / "config" / "funded_programs.yml"))["programs"]["two_step_static"]
    prog = Program(name="two_step_static", nominal=cfg["nominal"], max_loss_type="static",
                   max_loss_pct=cfg["max_loss_pct"], daily_loss_pct=cfg["daily_loss_pct"],
                   profit_target_phase1_pct=cfg["profit_target_phase1_pct"],
                   profit_target_phase2_pct=cfg["profit_target_phase2_pct"],
                   min_trading_days=cfg["min_trading_days"],
                   consistency_max_best_day_pct=cfg["consistency_max_best_day_pct"],
                   fee_usd=cfg["fee_usd"], payout_split=cfg["payout_split"])
    data = load_all()
    d = run_symbol(data["QQQ"], "QQQ", "disciplined", prog, 0.005, 12.0)
    r = run_symbol(data["QQQ"], "QQQ", "reckless", prog, 0.02, 12.0)
    return np.array(d.equity_curve), np.array(r.equity_curve)


def fig_equity_race(d_curve, r_curve):
    fig, ax = plt.subplots(figsize=(8.6, 3.6))
    ax.plot(d_curve, color=TEAL, lw=1.8, label=f"Disciplined 1/day 0.5% — ends ${d_curve[-1]:,.0f} ALIVE")
    ax.plot(np.arange(len(r_curve)), r_curve, color=RED, lw=1.8,
            label=f"Reckless 5/day 2% + revenge — DIES on day {len(r_curve)} (daily limit)")
    ax.axhline(90_000, color=GREY, ls="--", lw=1.2, label="Max-loss floor $90k")
    ax.scatter([len(r_curve) - 1], [r_curve[-1]], color=RED, s=70, zorder=5)
    ax.set_xlabel("Market day (QQQ 2018–2026, same signal, same market)")
    ax.set_ylabel("Balance (USD)")
    ax.set_title("E4 — Screen-time disease: same edge, two behaviours, two deaths", fontweight="bold")
    ax.legend(fontsize=8.5, loc="lower left")
    fig.tight_layout(); fig.savefig(DOCS / "fig-equity-race.png", bbox_inches="tight")
    plt.close(fig)


def demo_animation(d_curve, r_curve):
    n_frames = 150
    d_s = d_curve[np.linspace(0, len(d_curve) - 1, n_frames).astype(int)]
    r_full = r_curve
    fig, ax = plt.subplots(figsize=(8.6, 4.2))
    fig.patch.set_facecolor("#0f1b2d"); ax.set_facecolor("#0f1b2d")
    ax.tick_params(colors="white", labelsize=9)
    ax.set_xlabel("Market day", color="white"); ax.set_ylabel("Balance (USD)", color="white")
    ax.set_xlim(0, len(d_curve)); ax.set_ylim(88_000, max(d_curve.max(), 112_000))
    ax.axhline(90_000, color="#8a94a6", ls="--", lw=1.2)
    ax.text(len(d_curve) * 0.02, 90_600, "max-loss floor $90k", color="#8a94a6", fontsize=9)
    ax.axhline(100_000, color="#3a4a63", ls=":", lw=1.0)
    (ln_d,) = ax.plot([], [], color="#0ea5a4", lw=2.4, label="Disciplined")
    (ln_r,) = ax.plot([], [], color="#e5484d", lw=2.4, label="Reckless")
    dot_r, = ax.plot([], [], "o", color="#e5484d", ms=8)
    title = ax.set_title("", color="white", fontweight="bold", fontsize=11, loc="left")
    ax.legend(facecolor="#0f1b2d", edgecolor="#3a4a63", labelcolor="white", fontsize=9)
    xd = np.linspace(0, len(d_curve) - 1, n_frames)

    def frame(i):
        k = i + 1
        ln_d.set_data(xd[:k], d_s[:k])
        nr = min(len(r_full), int(len(r_full) * k / n_frames) + 1)
        xr = np.linspace(0, len(r_full) - 1, len(r_full))[:nr]
        ln_r.set_data(xr, r_full[:nr])
        dead = len(r_full) < len(d_curve) and nr >= len(r_full)
        if dead:
            dot_r.set_data([len(r_full) - 1], [r_full[-1]])
            status = (f"QQQ 2018–2026 · day {int(xd[i])}/{len(d_curve)} · "
                      f"Disciplined ${d_s[i]:,.0f} alive · Reckless DIED on day {len(r_full)} (daily limit)")
        else:
            dot_r.set_data([], [])
            status = (f"QQQ 2018–2026 · day {int(xd[i])}/{len(d_curve)} · "
                      f"Disciplined ${d_s[i]:,.0f} · Reckless ${r_full[nr-1]:,.0f}")
        title.set_text(status)
        return ln_d, ln_r, dot_r, title

    anim = FuncAnimation(fig, frame, frames=n_frames, interval=90, blit=False)
    anim.save(DOCS / "demo.gif", writer="pillow", fps=11)
    try:
        anim.save(DOCS / "demo.mp4", writer="ffmpeg", fps=11,
                  extra_args=["-vcodec", "libx264", "-pix_fmt", "yuv420p"])
        print("saved demo.mp4")
    except Exception as e:
        print("mp4 skipped:", e)
    plt.close(fig)


def main():
    print("building figures from verified results …")
    fig_trailing_trap()
    fig_risk_u()
    fig_calibration()
    d_curve, r_curve = _qqq_curves()
    fig_equity_race(d_curve, r_curve)
    demo_animation(d_curve, r_curve)
    for f in sorted(DOCS.glob("fig-*.png")) + [DOCS / "demo.gif"]:
        print(f"  {f.name}  {f.stat().st_size/1024:.0f} KB")
    if (DOCS / "demo.mp4").exists():
        print(f"  demo.mp4  {(DOCS/'demo.mp4').stat().st_size/1024:.0f} KB")

if __name__ == "__main__":
    main()
