"""Performance metrics: Sharpe / Sortino / Calmar / win-rate / DSR-lite."""
from __future__ import annotations

import numpy as np


def sharpe(daily: list[float] | np.ndarray) -> float:
    x = np.asarray(daily, dtype=float)
    if len(x) < 5 or x.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / x.std(ddof=1) * np.sqrt(252))


def sortino(daily) -> float:
    x = np.asarray(daily, dtype=float)
    dn = x[x < 0]
    if len(dn) < 5 or dn.std(ddof=1) == 0:
        return 0.0
    return float(x.mean() / dn.std(ddof=1) * np.sqrt(252))


def calmar(total_ret: float, max_dd_pct: float) -> float:
    if max_dd_pct <= 1e-9:
        return 0.0
    return float(total_ret * 100 / max_dd_pct)


def deflated_sharpe_lite(sr: float, n_trials: int, skew: float = 0.0, kurt: float = 3.0) -> float:
    """Bailey-Lopez de Prado DSR simplified gate: penalises many trials.
    Full DSR needs benchmark SR variance; here we return a haircut score in [0,1]
    for ranking, NOT a p-value. Documented as lite on purpose."""
    import math
    if n_trials <= 1:
        return max(0.0, min(1.0, 0.5 + sr / 4))
    haircut = math.sqrt(math.log(n_trials) / 2) * 0.15
    return max(0.0, min(1.0, 0.5 + (sr - haircut) / 4))
