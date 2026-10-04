"""Funded-account rule engine: static vs trailing, daily loss, consistency.

Implements exactly what Mo'men's video + 2026 help-centre research describe:
  - static floor: fixed at nominal*(1-max_loss_pct), never moves.
  - trailing_eod: floor = max(peak_close - max_loss, ...) ratchets on closes only,
    locks at nominal once peak clears nominal+max_loss (Apex/Topstep-style).
  - trailing_intraday: same but ratchets on equity highs incl. open P&L.
  - daily loss: max loss within one server day, measured on
    max(prev_close_balance, prev_close_equity) - daily_pct*basis.
    Commissions+swaps count (we deduct costs before checking).
  - consistency / best-day rule: best_day_pnl <= consistency_pct * total_pnl
    (else must keep trading; evaluation does NOT pass yet).
  - min trading days: evaluation needs >= min_days with a trade.

All money in USD. All checks on EQUITY (incl. floating) for strictness,
matching equity-based firms (harshest, most conservative for research).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Program:
    name: str
    nominal: float
    max_loss_type: str  # static | trailing_eod | trailing_intraday
    max_loss_pct: float
    daily_loss_pct: float
    profit_target_phase1_pct: float = 0.0
    profit_target_phase2_pct: float = 0.0
    min_trading_days: int = 0
    consistency_max_best_day_pct: float = 1.0
    fee_usd: float = 0.0
    payout_split: float = 0.8


@dataclass
class FundedAccount:
    prog: Program
    balance: float = 0.0
    peak_close: float = 0.0
    peak_equity: float = 0.0
    floor: float = 0.0
    day_start_ref: float = 0.0
    day_pnl: float = 0.0
    daily_pnls: list = field(default_factory=list)
    traded_days: set = field(default_factory=set)
    breached: str = ""
    total_fees_paid: float = 0.0

    def __post_init__(self):
        self.balance = self.prog.nominal
        self.peak_close = self.prog.nominal
        self.peak_equity = self.prog.nominal
        self.day_start_ref = self.prog.nominal
        max_loss = self.prog.nominal * self.prog.max_loss_pct
        self.floor = self.prog.nominal - max_loss
        self._max_loss_amt = max_loss

    # -- day management ---------------------------------------------------
    def start_day(self, ref_equity: float, ref_balance: float):
        # Mo'men secret 3: daily ref = higher of prev balance / equity
        self.day_start_ref = max(ref_balance, ref_equity)
        self.day_pnl = 0.0

    def end_day(self, close_balance: float):
        self.daily_pnls.append(self.day_pnl)
        if close_balance > self.peak_close:
            self.peak_close = close_balance
        if self.prog.max_loss_type == "trailing_eod":
            self._ratchet(close_balance)
        # EOD trailing locks at nominal once profit clears buffer (Topstep/Apex)
        # handled inside _ratchet

    def _ratchet(self, peak: float):
        lock = self.prog.nominal  # breakeven; real firms use start+$100 — we document the $100 variant
        if peak >= self.prog.nominal + self._max_loss_amt:
            candidate = lock  # freeze at breakeven: trailing converts to static
        else:
            candidate = peak - self._max_loss_amt
        if candidate > self.floor:
            self.floor = candidate

    # -- trade application -------------------------------------------------
    def apply_pnl(self, pnl: float, equity_now: float, date_str: str, is_close: bool = True):
        """Apply realised (or floating, if is_close False) PnL. Returns breach string or ''."""
        self.balance += pnl if is_close else 0.0
        self.day_pnl += pnl
        eq = equity_now
        if eq > self.peak_equity:
            self.peak_equity = eq
            if self.prog.max_loss_type == "trailing_intraday":
                self._ratchet(eq)
        if is_close and date_str:
            self.traded_days.add(date_str)
        # 1) max loss (equity basis — strictest, counts floating)
        if eq <= self.floor + 1e-9:
            self.breached = f"max_loss floor={self.floor:,.0f} equity={eq:,.0f}"
            return self.breached
        # 2) daily loss
        daily_floor = self.day_start_ref * (1 - self.prog.daily_loss_pct)
        if eq <= daily_floor + 1e-9:
            self.breached = f"daily_loss ref={self.day_start_ref:,.0f} floor={daily_floor:,.0f} equity={eq:,.0f}"
            return self.breached
        return ""

    # -- evaluation verdicts ----------------------------------------------
    def profit_pct(self) -> float:
        return (self.balance - self.prog.nominal) / self.prog.nominal

    def best_day_share(self) -> float:
        tot = sum(p for p in self.daily_pnls if p > 0)
        if tot <= 0:
            return 0.0
        best = max(self.daily_pnls) if self.daily_pnls else 0.0
        return best / tot if tot else 0.0

    def passes_target(self, phase: int = 1) -> tuple[bool, str]:
        tgt = self.prog.profit_target_phase1_pct if phase == 1 else self.prog.profit_target_phase2_pct
        if self.breached:
            return False, f"breached: {self.breached}"
        if self.profit_pct() < tgt - 1e-12:
            return False, f"target {tgt:.1%} not reached ({self.profit_pct():.2%})"
        if len(self.traded_days) < self.prog.min_trading_days:
            return False, f"min_days {len(self.traded_days)}/{self.prog.min_trading_days}"
        if self.best_day_share() > self.prog.consistency_max_best_day_pct + 1e-9:
            return False, (f"consistency: best-day {self.best_day_share():.1%} > "
                           f"{self.prog.consistency_max_best_day_pct:.0%}")
        return True, "PASS"

    @property
    def effective_capital(self) -> float:
        """Mo'men secret 1: real risk capital = max-loss distance, not nominal."""
        return self.prog.nominal * self.prog.max_loss_pct

    def leverage_illusion_ratio(self) -> float:
        return self.prog.nominal / self.effective_capital
