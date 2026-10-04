"""Unit tests for the funded rule engine — must pass before any claim is published."""
from src.funded_rules import FundedAccount, Program

def prog_static():
    return Program(name="t", nominal=100_000, max_loss_type="static",
                   max_loss_pct=0.10, daily_loss_pct=0.05)

def test_static_floor_never_moves():
    a = FundedAccount(prog_static())
    a.start_day(100_000, 100_000)
    assert a.apply_pnl(20_000, 120_000, "d") == ""
    a.end_day(120_000)
    assert a.floor == 90_000, a.floor

def test_static_breach():
    a = FundedAccount(prog_static())
    a.start_day(100_000, 100_000)
    # need equity <= floor AND daily floor: drop 10k breaches both; check max_loss text path via small daily
    p = Program(name="t", nominal=100_000, max_loss_type="static",
                max_loss_pct=0.10, daily_loss_pct=0.50)
    b = FundedAccount(p)
    b.start_day(100_000, 100_000)
    msg = b.apply_pnl(-10_000, 90_000, "d")
    assert "max_loss" in msg, msg

def test_trailing_eod_ratchets_and_locks():
    p = Program(name="t", nominal=100_000, max_loss_type="trailing_eod",
                max_loss_pct=0.10, daily_loss_pct=0.99)
    a = FundedAccount(p)
    a.start_day(100_000, 100_000)
    a.apply_pnl(5_000, 105_000, "d1")
    a.end_day(105_000)
    assert a.floor == 95_000, a.floor
    a.start_day(105_000, 105_000)
    a.apply_pnl(10_000, 115_000, "d2")
    a.end_day(115_000)
    assert a.floor == 100_000, a.floor  # locked at breakeven
    # pullback that static would survive kills trailing-before-lock? after lock behaves static
    assert a.apply_pnl(-9_000, 106_000, "d3") == ""

def test_daily_loss_counts_floating():
    a = FundedAccount(prog_static())
    a.start_day(100_000, 100_000)
    msg = a.apply_pnl(-5_000, 95_000, "d", is_close=False)
    assert "daily_loss" in msg, msg

def test_consistency_blocks_hero_day():
    p = Program(name="t", nominal=100_000, max_loss_type="static",
                max_loss_pct=0.10, daily_loss_pct=0.99,
                profit_target_phase1_pct=0.05, min_trading_days=1,
                consistency_max_best_day_pct=0.50)
    a = FundedAccount(p)
    bal = 100_000
    for i, pct in enumerate([0.05, 0.005]):
        pnl = pct * 100_000
        a.start_day(bal, bal)
        a.apply_pnl(pnl, bal + pnl, f"d{i}")
        a.end_day(bal + pnl)
        bal += pnl
    ok, reason = a.passes_target(1)
    assert not ok and "consistency" in reason, reason

def test_effective_capital():
    p = prog_static()
    a = FundedAccount(p)
    assert a.effective_capital == 10_000
    assert a.leverage_illusion_ratio() == 10.0
