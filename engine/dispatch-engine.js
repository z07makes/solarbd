// SolarThik Hybrid Dispatch Engine — JS port of dispatch_engine.py
//
// This is a faithful line-for-line port, not a reimplementation. Every constant
// and every branch of dispatch logic matches dispatch_engine.py exactly; see
// validate.py / validate-js.js for the cross-check proving the two agree.
// This port exists because the calculator and dashboard run in a browser —
// the Python file remains the reference implementation for any real backend /
// hardware-integration service.
//
// HARDENING PASS: forecast-aware reserve (setGenerationForecast), the
// tariff-agnostic scheduled resilience charge (resilienceChargeTargetFrac/
// resilienceChargeHour), and input validation (validateReading) are mirrored
// here to keep dispatch LOGIC identical between engines. Process-level
// concerns that only make sense server-side — state persistence to disk,
// Python `logging` — are NOT mirrored; a browser tab has no durable process
// to crash-recover, and console.warn stands in for structured logging here.
// See dispatch_engine.py's module docstring for the full rationale.

const RESIDENTIAL_SLABS = [
  [50, 4.63], [200, 7.50], [300, 9.10], [400, 9.62], [600, 15.01], [Infinity, 17.35]
]; // BERC June 2026 revision — sourced

const COMMERCIAL_FLAT_RATE = 15.36; // Tk/unit — sourced
const TOU_PEAK_RATE = 13.62;        // sourced (BCSA, 2025)
const TOU_OFFPEAK_RATE = 9.62;      // sourced
const TOU_PEAK_HOURS = new Set([18, 19, 20, 21, 22]); // illustrative 5h evening window
const BATTERY_COST_PER_KWH = 25000; // Tk/kWh, LiFePO4 — sourced

const TariffMode = Object.freeze({
  RESIDENTIAL_SLAB: 'residential_slab',
  COMMERCIAL_FLAT: 'commercial_flat',
  TIME_OF_USE: 'time_of_use',
});

function slabBill(unitsKwh) {
  if (unitsKwh <= 0) return 0;
  let remaining = unitsKwh, prevCap = 0, total = 0;
  for (const [cap, rate] of RESIDENTIAL_SLABS) {
    const band = cap - prevCap;
    const slabUnits = Math.min(remaining, band);
    if (slabUnits > 0) { total += slabUnits * rate; remaining -= slabUnits; }
    prevCap = cap;
    if (remaining <= 0) break;
  }
  return total;
}

function isPeakHour(mode, hour) {
  return mode === TariffMode.TIME_OF_USE && TOU_PEAK_HOURS.has(hour);
}

function instantaneousRate(mode, hour) {
  if (mode === TariffMode.COMMERCIAL_FLAT) return COMMERCIAL_FLAT_RATE;
  if (mode === TariffMode.TIME_OF_USE) return TOU_PEAK_HOURS.has(hour) ? TOU_PEAK_RATE : TOU_OFFPEAK_RATE;
  return null; // slab tariffs have no single well-defined instantaneous rate
}

class HybridDispatchEngine {
  constructor(config, initialSocKwh = null) {
    this.config = {
      resilienceReserveFrac: 0.15, peakHardFloorFrac: 0.05, chargeFromGridOffpeak: false,
      minReserveFrac: 0.15, maxReserveFrac: 0.60,
      resilienceChargeTargetFrac: null, resilienceChargeHour: null, resilienceChargeCutoffHour: null,
      ...config,
    };
    this.soc = initialSocKwh === null ? this.config.batteryCapacityKwh * 0.5 : initialSocKwh;
    this._effectiveReserveFrac = null; // set by setGenerationForecast()
    this._resetPeriodTotals();
  }

  setGenerationForecast(forecastKwhNextPeriod, baselineKwhPerPeriod) {
    if (!(baselineKwhPerPeriod > 0) || !(forecastKwhNextPeriod >= 0)) {
      console.warn(`setGenerationForecast: invalid baseline (${baselineKwhPerPeriod}) or forecast `
        + `(${forecastKwhNextPeriod}); falling back to the static resilienceReserveFrac`);
      this._effectiveReserveFrac = null;
      return this.config.resilienceReserveFrac;
    }
    const relative = forecastKwhNextPeriod / baselineKwhPerPeriod;
    const { minReserveFrac: lo, maxReserveFrac: hi, resilienceReserveFrac } = this.config;
    const raw = resilienceReserveFrac * (2.0 - relative);
    this._effectiveReserveFrac = Math.min(hi, Math.max(lo, raw));
    return this._effectiveReserveFrac;
  }

  clearGenerationForecast() {
    this._effectiveReserveFrac = null;
  }

  get activeReserveFrac() {
    return this._effectiveReserveFrac !== null ? this._effectiveReserveFrac : this.config.resilienceReserveFrac;
  }

  _resetPeriodTotals() {
    this.periodTotalLoadKwh = 0;
    this.periodTotalGridKwh = 0;
    this.periodPeakLoadKwh = 0;
    this.periodOffpeakLoadKwh = 0;
    this.periodPeakGridKwh = 0;
    this.periodOffpeakGridKwh = 0;
  }

  resetPeriod() { this._resetPeriodTotals(); }

  _periodSavings() {
    const mode = this.config.tariffMode;
    if (mode === TariffMode.RESIDENTIAL_SLAB) {
      return slabBill(this.periodTotalLoadKwh) - slabBill(this.periodTotalGridKwh);
    }
    if (mode === TariffMode.COMMERCIAL_FLAT) {
      return (this.periodTotalLoadKwh - this.periodTotalGridKwh) * COMMERCIAL_FLAT_RATE;
    }
    if (mode === TariffMode.TIME_OF_USE) {
      const counterfactual = this.periodPeakLoadKwh * TOU_PEAK_RATE + this.periodOffpeakLoadKwh * TOU_OFFPEAK_RATE;
      const actual = this.periodPeakGridKwh * TOU_PEAK_RATE + this.periodOffpeakGridKwh * TOU_OFFPEAK_RATE;
      return counterfactual - actual;
    }
    throw new Error(`Unknown tariff mode: ${mode}`);
  }

  scaledPeriodSavings(scaleFactor) {
    const mode = this.config.tariffMode;
    if (mode === TariffMode.RESIDENTIAL_SLAB) {
      return slabBill(this.periodTotalLoadKwh * scaleFactor) - slabBill(this.periodTotalGridKwh * scaleFactor);
    }
    if (mode === TariffMode.COMMERCIAL_FLAT) {
      return (this.periodTotalLoadKwh - this.periodTotalGridKwh) * scaleFactor * COMMERCIAL_FLAT_RATE;
    }
    if (mode === TariffMode.TIME_OF_USE) {
      const counterfactual = (this.periodPeakLoadKwh * TOU_PEAK_RATE + this.periodOffpeakLoadKwh * TOU_OFFPEAK_RATE) * scaleFactor;
      const actual = (this.periodPeakGridKwh * TOU_PEAK_RATE + this.periodOffpeakGridKwh * TOU_OFFPEAK_RATE) * scaleFactor;
      return counterfactual - actual;
    }
    throw new Error(`Unknown tariff mode: ${mode}`);
  }

  step(reading, dtHours) {
    const cfg = this.config;
    if (reading.batterySocKwh !== undefined && reading.batterySocKwh !== null) {
      this.soc = reading.batterySocKwh; // trust a real BMS reading over our own estimate
    }
    const net = reading.solarAvailableKw - reading.loadKw;
    const solarUsed = Math.min(reading.solarAvailableKw, reading.loadKw);
    let batteryKw = 0, gridKw = 0, unmetKw = 0, source;

    if (net >= 0) {
      const surplus = net;
      const headroomKwh = Math.max(0, cfg.batteryCapacityKwh - this.soc);
      const chargeKw = Math.min(surplus, cfg.batteryMaxRateKw, dtHours > 0 ? headroomKwh / dtHours : 0);
      batteryKw = -chargeKw;
      this.soc += chargeKw * dtHours;
      source = reading.loadKw > 0 ? 'solar' : 'solar (charging only)';
    } else {
      const deficit = -net;
      const peakNow = isPeakHour(cfg.tariffMode, reading.hour);
      let usableKwh;

      if (!reading.gridAvailable) {
        usableKwh = this.soc; // outage: resilience overrides everything, spend it all
      } else if (peakNow) {
        const floorKwh = cfg.batteryCapacityKwh * cfg.peakHardFloorFrac;
        usableKwh = Math.max(0, this.soc - floorKwh); // spend aggressively to shave the peak
      } else if (cfg.tariffMode === TariffMode.TIME_OF_USE) {
        usableKwh = 0; // TOU off-peak: hold everything back for the coming peak window
      } else {
        let reserveFrac = this.activeReserveFrac;
        if (cfg.resilienceChargeTargetFrac !== null && cfg.resilienceChargeHour !== null) {
          const cutoff = cfg.resilienceChargeCutoffHour;
          if (reading.hour >= cfg.resilienceChargeHour && (cutoff === null || reading.hour < cutoff)) {
            reserveFrac = Math.max(reserveFrac, cfg.resilienceChargeTargetFrac);
          }
        }
        const reserveKwh = cfg.batteryCapacityKwh * reserveFrac;
        usableKwh = Math.max(0, this.soc - reserveKwh);
      }

      const dischargeKw = Math.min(deficit, cfg.batteryMaxRateKw, dtHours > 0 ? usableKwh / dtHours : 0);
      this.soc -= dischargeKw * dtHours;
      batteryKw = dischargeKw;
      const remaining = deficit - dischargeKw;

      if (remaining > 1e-9) {
        if (reading.gridAvailable) {
          gridKw = remaining;
          if (cfg.tariffMode === TariffMode.TIME_OF_USE && !peakNow && cfg.chargeFromGridOffpeak
              && this.soc < cfg.batteryCapacityKwh) {
            const headroomKwh = cfg.batteryCapacityKwh - this.soc;
            const chargeKw = Math.min(cfg.batteryMaxRateKw, dtHours > 0 ? headroomKwh / dtHours : 0);
            batteryKw = -chargeKw;
            this.soc += chargeKw * dtHours;
            gridKw += chargeKw;
          }
          source = (solarUsed === 0 && batteryKw <= 0) ? 'grid' : 'solar+grid';
        } else {
          unmetKw = remaining;
          source = 'unmet (outage, battery exhausted)';
        }
      } else {
        source = solarUsed === 0 ? 'battery' : 'solar+battery';
      }
    }

    if (cfg.resilienceChargeTargetFrac !== null && cfg.resilienceChargeHour !== null
        && reading.gridAvailable && batteryKw <= 0) {
      const cutoff = cfg.resilienceChargeCutoffHour;
      const inWindow = reading.hour >= cfg.resilienceChargeHour && (cutoff === null || reading.hour < cutoff);
      if (inWindow) {
        const targetKwh = cfg.batteryCapacityKwh * cfg.resilienceChargeTargetFrac;
        if (this.soc < targetKwh) {
          const alreadyChargingKw = -batteryKw;
          const rateHeadroomKw = Math.max(0, cfg.batteryMaxRateKw - alreadyChargingKw);
          const headroomKwh = targetKwh - this.soc;
          const extraChargeKw = Math.min(rateHeadroomKw, dtHours > 0 ? headroomKwh / dtHours : 0);
          if (extraChargeKw > 1e-9) {
            this.soc += extraChargeKw * dtHours;
            batteryKw -= extraChargeKw;
            gridKw += extraChargeKw;
            source = solarUsed > 0 ? 'solar+grid (resilience charge)' : 'grid (resilience charge)';
          }
        }
      }
    }

    if (reading.gridAvailable) {
      this.periodTotalLoadKwh += reading.loadKw * dtHours;
      this.periodTotalGridKwh += gridKw * dtHours;
      if (isPeakHour(cfg.tariffMode, reading.hour)) {
        this.periodPeakLoadKwh += reading.loadKw * dtHours;
        this.periodPeakGridKwh += gridKw * dtHours;
      } else {
        this.periodOffpeakLoadKwh += reading.loadKw * dtHours;
        this.periodOffpeakGridKwh += gridKw * dtHours;
      }
    }

    return {
      source, solarUsedKw: solarUsed, batteryKw, gridKw, unmetKw,
      batterySocKwh: this.soc,
      gridRateTk: instantaneousRate(cfg.tariffMode, reading.hour),
      savingsSoFarTk: this._periodSavings(),
    };
  }

  toState() {
    return {
      soc: this.soc,
      effectiveReserveFrac: this._effectiveReserveFrac,
      periodTotalLoadKwh: this.periodTotalLoadKwh,
      periodTotalGridKwh: this.periodTotalGridKwh,
      periodPeakLoadKwh: this.periodPeakLoadKwh,
      periodOffpeakLoadKwh: this.periodOffpeakLoadKwh,
      periodPeakGridKwh: this.periodPeakGridKwh,
      periodOffpeakGridKwh: this.periodOffpeakGridKwh,
    };
  }

  loadState(state) {
    this.soc = state.soc;
    this._effectiveReserveFrac = state.effectiveReserveFrac ?? null;
    this.periodTotalLoadKwh = state.periodTotalLoadKwh;
    this.periodTotalGridKwh = state.periodTotalGridKwh;
    this.periodPeakLoadKwh = state.periodPeakLoadKwh;
    this.periodOffpeakLoadKwh = state.periodOffpeakLoadKwh;
    this.periodPeakGridKwh = state.periodPeakGridKwh;
    this.periodOffpeakGridKwh = state.periodOffpeakGridKwh;
  }

  static fromState(config, state) {
    const engine = new HybridDispatchEngine(config, state.soc);
    engine.loadState(state);
    return engine;
  }
}

const ReadingFault = Object.freeze({
  NEGATIVE_SOLAR: 'negative_solar_clipped_to_zero',
  NEGATIVE_LOAD: 'negative_load_clipped_to_zero',
  NON_FINITE_VALUE: 'non_finite_value_clipped_to_zero',
  SOC_OUT_OF_RANGE: 'battery_soc_clamped_to_capacity_bounds',
  HOUR_OUT_OF_RANGE: 'hour_normalized_to_0_23',
});

function validateReading(reading, { batteryCapacityKwh = null, sourceId = 'unknown' } = {}) {
  const faults = [];
  let { hour, solarAvailableKw: solar, loadKw: load, gridAvailable, batterySocKwh: soc } = reading;

  const finite = (x) => Number.isFinite(x);

  if (!finite(solar)) { faults.push(ReadingFault.NON_FINITE_VALUE); solar = 0; }
  else if (solar < 0) { faults.push(ReadingFault.NEGATIVE_SOLAR); solar = 0; }

  if (!finite(load)) { faults.push(ReadingFault.NON_FINITE_VALUE); load = 0; }
  else if (load < 0) { faults.push(ReadingFault.NEGATIVE_LOAD); load = 0; }

  if (!(hour >= 0 && hour <= 23)) { faults.push(ReadingFault.HOUR_OUT_OF_RANGE); hour = ((hour % 24) + 24) % 24; }

  if (soc !== undefined && soc !== null && batteryCapacityKwh !== null) {
    if (!finite(soc) || soc < 0 || soc > batteryCapacityKwh) {
      faults.push(ReadingFault.SOC_OUT_OF_RANGE);
      soc = !finite(soc) ? null : Math.min(Math.max(soc, 0), batteryCapacityKwh);
    }
  }

  return {
    cleaned: { hour, solarAvailableKw: solar, loadKw: load, gridAvailable, batterySocKwh: soc },
    faults,
  };
}

const FeedStatus = Object.freeze({ OK: 'ok', STALE: 'stale', NEVER_SEEN: 'never_seen' });

class TelemetryWatchdog {
  constructor(maxStalenessS = 30.0) {
    this.maxStalenessS = maxStalenessS;
    this._lastReading = null;
    this._lastSeenMs = null;
  }
  ingest(reading, _now = null) {
    this._lastReading = reading;
    this._lastSeenMs = _now === null ? Date.now() : _now;
  }
  status(_now = null) {
    if (this._lastSeenMs === null) return FeedStatus.NEVER_SEEN;
    const now = _now === null ? Date.now() : _now;
    const ageS = (now - this._lastSeenMs) / 1000;
    return ageS > this.maxStalenessS ? FeedStatus.STALE : FeedStatus.OK;
  }
  get lastReading() { return this._lastReading; }
}

function solarShape(hour, peakKw) {
  if (hour < 6 || hour >= 18) return 0;
  return peakKw * Math.sin(((hour - 6) / 12) * Math.PI);
}

function buildSolarProfile(dailyGenerationKwhTarget) {
  const rawHours = [];
  for (let h = 6; h < 18; h++) rawHours.push(h);
  const rawTotal = rawHours.reduce((a, h) => a + solarShape(h, 1.0), 0);
  const peakKw = rawTotal > 0 ? dailyGenerationKwhTarget / rawTotal : 0;
  const profile = new Array(24).fill(0);
  for (let h = 0; h < 24; h++) profile[h] = solarShape(h, peakKw);
  return profile;
}

function simulateDay(dailyGenerationKwhTarget, loadShapeKw, gridAvailableHours = null, stepsPerHour = 12) {
  const solarProfile = buildSolarProfile(dailyGenerationKwhTarget);
  const dt = 1 / stepsPerHour;
  const readings = [];
  for (let h = 0; h < 24; h++) {
    const solarKw = solarProfile[h];
    const loadKw = loadShapeKw[h];
    const gridOk = gridAvailableHours === null ? true : gridAvailableHours.has(h);
    for (let s = 0; s < stepsPerHour; s++) {
      readings.push({ hour: h, solarAvailableKw: solarKw, loadKw, gridAvailable: gridOk });
    }
  }
  return { readings, dt };
}

function runReadings(engine, readings, dt) {
  return readings.map(r => engine.step(r, dt));
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    TariffMode, slabBill, isPeakHour, instantaneousRate, HybridDispatchEngine,
    solarShape, buildSolarProfile, simulateDay, runReadings, BATTERY_COST_PER_KWH,
    RESIDENTIAL_SLABS, COMMERCIAL_FLAT_RATE, TOU_PEAK_RATE, TOU_OFFPEAK_RATE, TOU_PEAK_HOURS,
    validateReading, ReadingFault, TelemetryWatchdog, FeedStatus,
  };
}
