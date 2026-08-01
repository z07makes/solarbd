const {
  HybridDispatchEngine, TariffMode, buildSolarProfile, solarShape, slabBill, validateReading,
} = require('./dispatch-engine.js');

function runPoultryTestF() {
  const cfg = {
    batteryCapacityKwh: 2.4, batteryMaxRateKw: 1.6, tariffMode: TariffMode.COMMERCIAL_FLAT,
    resilienceChargeTargetFrac: 0.95, resilienceChargeHour: 11, resilienceChargeCutoffHour: 19,
  };
  const engine = new HybridDispatchEngine(cfg, 2.4 * 0.5);
  const stepsPerHour = 12, dt = 1 / stepsPerHour;
  const solarFor = (h) => solarShape(h, 1.36);
  for (let h = 0; h < 24; h++) for (let s = 0; s < stepsPerHour; s++) {
    engine.step({ hour: h, solarAvailableKw: solarFor(h), loadKw: 1.35, gridAvailable: true }, dt);
  }
  engine.resetPeriod();
  for (let h = 0; h < 24; h++) for (let s = 0; s < stepsPerHour; s++) {
    engine.step({ hour: h, solarAvailableKw: solarFor(h), loadKw: 1.35, gridAvailable: true }, dt);
  }
  return engine.scaledPeriodSavings(30.4);
}

function runColdStorage(battCap, battRate) {
  const cfg = {
    batteryCapacityKwh: battCap, batteryMaxRateKw: battRate, tariffMode: TariffMode.TIME_OF_USE,
    peakHardFloorFrac: 0.05, chargeFromGridOffpeak: true,
  };
  const engine = new HybridDispatchEngine(cfg, 0);
  const solarByHour = buildSolarProfile(100 * 4.3 * 0.8);
  const load = 3000 * 800 / 8760;
  const stepsPerHour = 12, dt = 1 / stepsPerHour;
  for (let day = 0; day < 2; day++) {
    for (let h = 0; h < 24; h++) for (let s = 0; s < stepsPerHour; s++) {
      engine.step({ hour: h, solarAvailableKw: solarByHour[h], loadKw: load, gridAvailable: true }, dt);
    }
    if (day === 0) engine.resetPeriod();
  }
  return engine.scaledPeriodSavings(30.4);
}

function runForecastReserve() {
  const engine = new HybridDispatchEngine({ batteryCapacityKwh: 10, batteryMaxRateKw: 5, tariffMode: TariffMode.RESIDENTIAL_SLAB });
  const noForecast = engine.activeReserveFrac;
  const withForecast = engine.setGenerationForecast(0.45 * 10, 10);
  engine.clearGenerationForecast();
  const afterClear = engine.activeReserveFrac;
  return { noForecast, withForecast, afterClear };
}

function runValidateReadingSanity() {
  return validateReading(
    { hour: 25, solarAvailableKw: -2, loadKw: NaN, gridAvailable: true, batterySocKwh: 999 },
    { batteryCapacityKwh: 10, sourceId: 'test' },
  );
}

const results = {
  poultryTestF: runPoultryTestF(),
  coldStorage0: runColdStorage(0, 0),
  coldStorage500: runColdStorage(500, 150),
  coldStorage1000: runColdStorage(1000, 250),
  coldStorage1500: runColdStorage(1500, 300),
  forecastReserve: runForecastReserve(),
  slabBilling800: slabBill(800),
  validateReadingSanity: runValidateReadingSanity(),
};
console.log(JSON.stringify(results));
