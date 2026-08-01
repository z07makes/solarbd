"""
SolarThik Hybrid Dispatch Engine — Python reference implementation.

PROVENANCE NOTE — read this before treating this file as historical record.
This file did not exist anywhere in the SolarThik project history available
to this conversation: not uploaded in any session, not in the GitHub repo
(github.com/z07makes/solarbd — confirmed by a live clone on 2026-08-01, still
a single "Initial commit" with none of the engine files), and not embedded in
SOLARTHIK-MASTER-REPOSITORY.md. dispatch-engine.js's own header comment
describes itself as "a faithful line-for-line port" of this file, but this
file was never actually provided to back that claim up.

This version was authored fresh, as a faithful, logic-for-logic port of the
verified dispatch-engine.js (the JS file embedded verbatim in that master
document's Appendix A1, cross-checked test-by-test across multiple prior
sessions). The direction of translation ran JS -> Python this time, the
reverse of what the original project history assumed. Every constant,
branch, and rationale comment has been preserved; naming was adapted to
Python convention (snake_case, a Reading dataclass instead of a plain
object). It has been cross-validated against dispatch-engine.js by running
both engines on identical scenarios and diffing the output numerically —
see cross_check_js_python.py in this same delivery. Treat this file as newly
authored and freshly verified, not as a recovered original. If an actual
original dispatch_engine.py turns up anywhere else (an old backup, a
different machine), that file is the one to reconcile against, not this one.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# TARIFF CONSTANTS
# ---------------------------------------------------------------------------

RESIDENTIAL_SLABS: List[Tuple[float, float]] = [
    (50, 4.63), (200, 7.50), (300, 9.10), (400, 9.62), (600, 15.01), (float("inf"), 17.35),
]  # BERC June 2026 revision — sourced

COMMERCIAL_FLAT_RATE = 15.36  # Tk/unit — sourced
TOU_PEAK_RATE = 13.62         # sourced (BCSA, 2025)
TOU_OFFPEAK_RATE = 9.62       # sourced
TOU_PEAK_HOURS = frozenset({18, 19, 20, 21, 22})  # illustrative 5h evening window
BATTERY_COST_PER_KWH = 25000  # Tk/kWh, LiFePO4 — sourced


class TariffMode:
    RESIDENTIAL_SLAB = "residential_slab"
    COMMERCIAL_FLAT = "commercial_flat"
    TIME_OF_USE = "time_of_use"


def slab_bill(units_kwh: float) -> float:
    if units_kwh <= 0:
        return 0.0
    remaining, prev_cap, total = units_kwh, 0.0, 0.0
    for cap, rate in RESIDENTIAL_SLABS:
        band = cap - prev_cap
        slab_units = min(remaining, band)
        if slab_units > 0:
            total += slab_units * rate
            remaining -= slab_units
        prev_cap = cap
        if remaining <= 0:
            break
    return total


def is_peak_hour(mode: str, hour: int) -> bool:
    return mode == TariffMode.TIME_OF_USE and hour in TOU_PEAK_HOURS


def instantaneous_rate(mode: str, hour: int) -> Optional[float]:
    if mode == TariffMode.COMMERCIAL_FLAT:
        return COMMERCIAL_FLAT_RATE
    if mode == TariffMode.TIME_OF_USE:
        return TOU_PEAK_RATE if hour in TOU_PEAK_HOURS else TOU_OFFPEAK_RATE
    return None  # slab tariffs have no single well-defined instantaneous rate


@dataclass
class Reading:
    hour: int
    solar_available_kw: float
    load_kw: float
    grid_available: bool
    battery_soc_kwh: Optional[float] = None


@dataclass
class DispatchResult:
    source: str
    solar_used_kw: float
    battery_kw: float
    grid_kw: float
    unmet_kw: float
    battery_soc_kwh: float
    grid_rate_tk: Optional[float]
    savings_so_far_tk: float


_DEFAULT_CONFIG = dict(
    resilience_reserve_frac=0.15,
    peak_hard_floor_frac=0.05,
    charge_from_grid_offpeak=False,
    min_reserve_frac=0.15,
    max_reserve_frac=0.60,
    resilience_charge_target_frac=None,
    resilience_charge_hour=None,
    resilience_charge_cutoff_hour=None,
)


class HybridDispatchEngine:
    """
    config keys (required unless noted): battery_capacity_kwh, battery_max_rate_kw,
    tariff_mode (one of TariffMode). Optional, with defaults above:
    resilience_reserve_frac, peak_hard_floor_frac, charge_from_grid_offpeak,
    min_reserve_frac, max_reserve_frac, resilience_charge_target_frac,
    resilience_charge_hour, resilience_charge_cutoff_hour.
    """

    def __init__(self, config: Dict[str, Any], initial_soc_kwh: Optional[float] = None):
        merged = dict(_DEFAULT_CONFIG)
        merged.update(config)
        self.config = merged
        self.soc = (self.config["battery_capacity_kwh"] * 0.5) if initial_soc_kwh is None else initial_soc_kwh
        self._effective_reserve_frac: Optional[float] = None  # set by set_generation_forecast()
        self._reset_period_totals()

    def set_generation_forecast(self, forecast_kwh_next_period: float, baseline_kwh_per_period: float) -> float:
        """
        Heuristic, not a rolling-horizon optimizer; degrades safely to the
        static resilience_reserve_frac when no forecast is set. Returns the
        effective reserve fraction now in effect.
        """
        if not (baseline_kwh_per_period > 0) or not (forecast_kwh_next_period >= 0):
            self._effective_reserve_frac = None
            return self.config["resilience_reserve_frac"]
        relative = forecast_kwh_next_period / baseline_kwh_per_period
        lo, hi = self.config["min_reserve_frac"], self.config["max_reserve_frac"]
        base = self.config["resilience_reserve_frac"]
        raw = base * (2.0 - relative)
        self._effective_reserve_frac = min(hi, max(lo, raw))
        return self._effective_reserve_frac

    def clear_generation_forecast(self) -> None:
        """Reverts to the static resilience_reserve_frac -- e.g. if the
        forecast feed goes down. Fail-safe default, not fail-open."""
        self._effective_reserve_frac = None

    @property
    def active_reserve_frac(self) -> float:
        """What reserve fraction step() will actually use right now."""
        if self._effective_reserve_frac is not None:
            return self._effective_reserve_frac
        return self.config["resilience_reserve_frac"]

    def _reset_period_totals(self) -> None:
        self.period_total_load_kwh = 0.0
        self.period_total_grid_kwh = 0.0
        self.period_peak_load_kwh = 0.0
        self.period_offpeak_load_kwh = 0.0
        self.period_peak_grid_kwh = 0.0
        self.period_offpeak_grid_kwh = 0.0

    def reset_period(self) -> None:
        self._reset_period_totals()

    def _period_savings(self) -> float:
        mode = self.config["tariff_mode"]
        if mode == TariffMode.RESIDENTIAL_SLAB:
            return slab_bill(self.period_total_load_kwh) - slab_bill(self.period_total_grid_kwh)
        if mode == TariffMode.COMMERCIAL_FLAT:
            return (self.period_total_load_kwh - self.period_total_grid_kwh) * COMMERCIAL_FLAT_RATE
        if mode == TariffMode.TIME_OF_USE:
            counterfactual = self.period_peak_load_kwh * TOU_PEAK_RATE + self.period_offpeak_load_kwh * TOU_OFFPEAK_RATE
            actual = self.period_peak_grid_kwh * TOU_PEAK_RATE + self.period_offpeak_grid_kwh * TOU_OFFPEAK_RATE
            return counterfactual - actual
        raise ValueError(f"Unknown tariff mode: {mode}")

    def scaled_period_savings(self, scale_factor: float) -> float:
        """
        Extrapolates a simulated period (e.g. one representative day) to a
        longer one (e.g. a month) CORRECTLY for slab tariffs. Scaling an
        already-computed slab-tariff Tk figure by a day-count multiplier is
        wrong, because slab billing is non-linear in volume. The right move
        is to scale the physical kWh totals first, then bill once. For
        flat/TOU tariffs (linear in volume) both approaches agree, so this
        is always the correct method to call.
        """
        mode = self.config["tariff_mode"]
        if mode == TariffMode.RESIDENTIAL_SLAB:
            return slab_bill(self.period_total_load_kwh * scale_factor) - slab_bill(self.period_total_grid_kwh * scale_factor)
        if mode == TariffMode.COMMERCIAL_FLAT:
            return (self.period_total_load_kwh - self.period_total_grid_kwh) * scale_factor * COMMERCIAL_FLAT_RATE
        if mode == TariffMode.TIME_OF_USE:
            counterfactual = (self.period_peak_load_kwh * TOU_PEAK_RATE + self.period_offpeak_load_kwh * TOU_OFFPEAK_RATE) * scale_factor
            actual = (self.period_peak_grid_kwh * TOU_PEAK_RATE + self.period_offpeak_grid_kwh * TOU_OFFPEAK_RATE) * scale_factor
            return counterfactual - actual
        raise ValueError(f"Unknown tariff mode: {mode}")

    def step(self, reading: Reading, dt_hours: float) -> DispatchResult:
        cfg = self.config
        if reading.battery_soc_kwh is not None:
            self.soc = reading.battery_soc_kwh  # trust a real BMS reading over our own estimate

        net = reading.solar_available_kw - reading.load_kw
        solar_used = min(reading.solar_available_kw, reading.load_kw)
        battery_kw = 0.0
        grid_kw = 0.0
        unmet_kw = 0.0
        source = ""

        if net >= 0:
            surplus = net
            headroom_kwh = max(0.0, cfg["battery_capacity_kwh"] - self.soc)
            charge_kw = min(surplus, cfg["battery_max_rate_kw"], (headroom_kwh / dt_hours) if dt_hours > 0 else 0.0)
            battery_kw = -charge_kw
            self.soc += charge_kw * dt_hours
            # any (surplus - charge_kw) beyond headroom/rate is exported or curtailed --
            # not modelled as a feed-in credit (conservative).
            source = "solar" if reading.load_kw > 0 else "solar (charging only)"
        else:
            deficit = -net
            peak_now = is_peak_hour(cfg["tariff_mode"], reading.hour)

            if not reading.grid_available:
                usable_kwh = self.soc  # outage: resilience overrides everything, spend it all
            elif peak_now:
                floor_kwh = cfg["battery_capacity_kwh"] * cfg["peak_hard_floor_frac"]
                usable_kwh = max(0.0, self.soc - floor_kwh)  # spend aggressively to shave the peak
            elif cfg["tariff_mode"] == TariffMode.TIME_OF_USE:
                usable_kwh = 0.0  # TOU off-peak: hold everything back for the coming peak window
            else:
                # Flat or slab tariff: no peak window exists to protect the battery FOR,
                # so discharge normally, respecting only the resilience reserve --
                # forecast-adjusted if set_generation_forecast() was called this period.
                #
                # During a configured scheduled resilience-charge window, this floor is
                # temporarily RAISED to that window's target fraction -- otherwise the
                # grid top-up added below would be spent right back down by this same
                # "discharge to the ordinary floor" policy on the very next tick.
                reserve_frac = self.active_reserve_frac
                if cfg["resilience_charge_target_frac"] is not None and cfg["resilience_charge_hour"] is not None:
                    cutoff = cfg["resilience_charge_cutoff_hour"]
                    if reading.hour >= cfg["resilience_charge_hour"] and (cutoff is None or reading.hour < cutoff):
                        reserve_frac = max(reserve_frac, cfg["resilience_charge_target_frac"])
                reserve_kwh = cfg["battery_capacity_kwh"] * reserve_frac
                usable_kwh = max(0.0, self.soc - reserve_kwh)

            discharge_kw = min(deficit, cfg["battery_max_rate_kw"], (usable_kwh / dt_hours) if dt_hours > 0 else 0.0)
            self.soc -= discharge_kw * dt_hours
            battery_kw = discharge_kw
            remaining = deficit - discharge_kw

            if remaining > 1e-9:
                if reading.grid_available:
                    grid_kw = remaining
                    if (cfg["tariff_mode"] == TariffMode.TIME_OF_USE and not peak_now
                            and cfg["charge_from_grid_offpeak"] and self.soc < cfg["battery_capacity_kwh"]):
                        headroom_kwh = cfg["battery_capacity_kwh"] - self.soc
                        charge_kw = min(cfg["battery_max_rate_kw"], (headroom_kwh / dt_hours) if dt_hours > 0 else 0.0)
                        battery_kw = -charge_kw
                        self.soc += charge_kw * dt_hours
                        grid_kw += charge_kw  # extra off-peak draw to charge for the peak window -- honestly accounted
                    source = "grid" if (solar_used == 0 and battery_kw <= 0) else "solar+grid"
                else:
                    unmet_kw = remaining
                    source = "unmet (outage, battery exhausted)"
            else:
                source = "battery" if solar_used == 0 else "solar+battery"

        # Scheduled resilience charge (tariff-agnostic). Applied ONLY on top of an
        # idle-or-charging outcome from the block above (battery_kw <= 0) -- it never
        # overrides an active discharge in the same tick, so it stays auditable as a
        # pure top-up. This is what lets a flat- or slab-tariff customer with a thin
        # solar-over-load margin still reach a known SOC before a recurring risk window.
        if (cfg["resilience_charge_target_frac"] is not None and cfg["resilience_charge_hour"] is not None
                and reading.grid_available and battery_kw <= 0):
            cutoff = cfg["resilience_charge_cutoff_hour"]
            in_window = reading.hour >= cfg["resilience_charge_hour"] and (cutoff is None or reading.hour < cutoff)
            if in_window:
                target_kwh = cfg["battery_capacity_kwh"] * cfg["resilience_charge_target_frac"]
                if self.soc < target_kwh:
                    already_charging_kw = -battery_kw  # 0 if idle, >0 if solar was already charging
                    rate_headroom_kw = max(0.0, cfg["battery_max_rate_kw"] - already_charging_kw)
                    headroom_kwh = target_kwh - self.soc
                    extra_charge_kw = min(rate_headroom_kw, (headroom_kwh / dt_hours) if dt_hours > 0 else 0.0)
                    if extra_charge_kw > 1e-9:
                        self.soc += extra_charge_kw * dt_hours
                        battery_kw -= extra_charge_kw
                        grid_kw += extra_charge_kw  # honestly accounted as an extra grid draw
                        source = "solar+grid (resilience charge)" if solar_used > 0 else "grid (resilience charge)"

        # Billing-relevant totals only accumulate when the grid is actually up: during
        # an outage, nobody gets billed for grid power, so outage-period load must NOT
        # enter the savings counterfactual. Unmet load is tracked separately for a
        # resilience-specific metric.
        if reading.grid_available:
            self.period_total_load_kwh += reading.load_kw * dt_hours
            self.period_total_grid_kwh += grid_kw * dt_hours
            if is_peak_hour(cfg["tariff_mode"], reading.hour):
                self.period_peak_load_kwh += reading.load_kw * dt_hours
                self.period_peak_grid_kwh += grid_kw * dt_hours
            else:
                self.period_offpeak_load_kwh += reading.load_kw * dt_hours
                self.period_offpeak_grid_kwh += grid_kw * dt_hours

        return DispatchResult(
            source=source, solar_used_kw=solar_used, battery_kw=battery_kw, grid_kw=grid_kw, unmet_kw=unmet_kw,
            battery_soc_kwh=self.soc, grid_rate_tk=instantaneous_rate(cfg["tariff_mode"], reading.hour),
            savings_so_far_tk=self._period_savings(),
        )

    def to_state(self) -> Dict[str, Any]:
        return dict(
            soc=self.soc,
            effective_reserve_frac=self._effective_reserve_frac,
            period_total_load_kwh=self.period_total_load_kwh,
            period_total_grid_kwh=self.period_total_grid_kwh,
            period_peak_load_kwh=self.period_peak_load_kwh,
            period_offpeak_load_kwh=self.period_offpeak_load_kwh,
            period_peak_grid_kwh=self.period_peak_grid_kwh,
            period_offpeak_grid_kwh=self.period_offpeak_grid_kwh,
        )

    def load_state(self, state: Dict[str, Any]) -> None:
        self.soc = state["soc"]
        self._effective_reserve_frac = state.get("effective_reserve_frac")
        self.period_total_load_kwh = state["period_total_load_kwh"]
        self.period_total_grid_kwh = state["period_total_grid_kwh"]
        self.period_peak_load_kwh = state["period_peak_load_kwh"]
        self.period_offpeak_load_kwh = state["period_offpeak_load_kwh"]
        self.period_peak_grid_kwh = state["period_peak_grid_kwh"]
        self.period_offpeak_grid_kwh = state["period_offpeak_grid_kwh"]

    @classmethod
    def from_state(cls, config: Dict[str, Any], state: Dict[str, Any]) -> "HybridDispatchEngine":
        engine = cls(config, state["soc"])
        engine.load_state(state)
        return engine


# ---------------------------------------------------------------------------
# INPUT VALIDATION & TELEMETRY FAULT HANDLING
# ---------------------------------------------------------------------------

class ReadingFault:
    NEGATIVE_SOLAR = "negative_solar_clipped_to_zero"
    NEGATIVE_LOAD = "negative_load_clipped_to_zero"
    NON_FINITE_VALUE = "non_finite_value_clipped_to_zero"
    SOC_OUT_OF_RANGE = "battery_soc_clamped_to_capacity_bounds"
    HOUR_OUT_OF_RANGE = "hour_normalized_to_0_23"


def _finite(x: Any) -> bool:
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)


def validate_reading(
    reading: Reading, battery_capacity_kwh: Optional[float] = None, source_id: str = "unknown"
) -> Tuple[Reading, List[str]]:
    faults: List[str] = []
    hour = reading.hour
    solar = reading.solar_available_kw
    load = reading.load_kw
    soc = reading.battery_soc_kwh

    if not _finite(solar):
        faults.append(ReadingFault.NON_FINITE_VALUE)
        solar = 0.0
    elif solar < 0:
        faults.append(ReadingFault.NEGATIVE_SOLAR)
        solar = 0.0

    if not _finite(load):
        faults.append(ReadingFault.NON_FINITE_VALUE)
        load = 0.0
    elif load < 0:
        faults.append(ReadingFault.NEGATIVE_LOAD)
        load = 0.0

    if not (0 <= hour <= 23):
        faults.append(ReadingFault.HOUR_OUT_OF_RANGE)
        hour = ((hour % 24) + 24) % 24

    if soc is not None and battery_capacity_kwh is not None:
        if not _finite(soc) or soc < 0 or soc > battery_capacity_kwh:
            faults.append(ReadingFault.SOC_OUT_OF_RANGE)
            soc = None if not _finite(soc) else min(max(soc, 0.0), battery_capacity_kwh)

    cleaned = Reading(hour=hour, solar_available_kw=solar, load_kw=load,
                       grid_available=reading.grid_available, battery_soc_kwh=soc)
    return cleaned, faults


class FeedStatus:
    OK = "ok"
    STALE = "stale"
    NEVER_SEEN = "never_seen"


class TelemetryWatchdog:
    """Enforces 'silence is not zero': a missing feed is a fault, not zero
    generation/load. Uses time.time() by default; pass _now for deterministic tests."""

    def __init__(self, max_staleness_s: float = 30.0):
        self.max_staleness_s = max_staleness_s
        self._last_reading: Optional[Reading] = None
        self._last_seen_s: Optional[float] = None

    def ingest(self, reading: Reading, _now: Optional[float] = None) -> None:
        self._last_reading = reading
        self._last_seen_s = time.time() if _now is None else _now

    def status(self, _now: Optional[float] = None) -> str:
        if self._last_seen_s is None:
            return FeedStatus.NEVER_SEEN
        now = time.time() if _now is None else _now
        age_s = now - self._last_seen_s
        return FeedStatus.STALE if age_s > self.max_staleness_s else FeedStatus.OK

    @property
    def last_reading(self) -> Optional[Reading]:
        return self._last_reading


# ---------------------------------------------------------------------------
# SIMULATOR helpers
# ---------------------------------------------------------------------------

def solar_shape(hour: int, peak_kw: float) -> float:
    if hour < 6 or hour >= 18:
        return 0.0
    return peak_kw * math.sin(((hour - 6) / 12) * math.pi)


def build_solar_profile(daily_generation_kwh_target: float) -> List[float]:
    raw_hours = list(range(6, 18))
    raw_total = sum(solar_shape(h, 1.0) for h in raw_hours)
    peak_kw = (daily_generation_kwh_target / raw_total) if raw_total > 0 else 0.0
    return [solar_shape(h, peak_kw) for h in range(24)]


def simulate_day(
    daily_generation_kwh_target: float, load_shape_kw: List[float],
    grid_available_hours: Optional[set] = None, steps_per_hour: int = 12,
) -> Tuple[List[Reading], float]:
    solar_profile = build_solar_profile(daily_generation_kwh_target)
    dt = 1 / steps_per_hour
    readings: List[Reading] = []
    for h in range(24):
        solar_kw = solar_profile[h]
        load_kw = load_shape_kw[h]
        grid_ok = True if grid_available_hours is None else (h in grid_available_hours)
        for _ in range(steps_per_hour):
            readings.append(Reading(hour=h, solar_available_kw=solar_kw, load_kw=load_kw, grid_available=grid_ok))
    return readings, dt


def run_readings(engine: HybridDispatchEngine, readings: List[Reading], dt: float) -> List[DispatchResult]:
    return [engine.step(r, dt) for r in readings]
