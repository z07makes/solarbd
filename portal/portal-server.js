// SolarThik lender/integrator portal — MINIMAL backend reference implementation
//
// WHAT THIS FIXES: in solarthik-platform-prototype.html, the full PORTFOLIO
// array sits in browser memory and the "integrator view" is just
// `PORTFOLIO.filter(r => r.integrator === INTEGRATOR_NAME)` run in the client.
// Any authenticated user could open dev tools and read every customer's data
// across every segment, regardless of which view they're supposed to see.
//
// THE FIX: the client never receives rows it isn't allowed to see. Scoping
// happens here, server-side, based on a verified JWT — not on data the
// browser can inspect or a filter the browser can skip.
//
// WHAT THIS IS NOT: a complete auth system. /api/login below issues a token
// for any {role, integratorName} you send it — that's a stand-in for real
// credential verification (a password check against a hashed value in a real
// user table, ideally behind your bank/NBFI's or integrator's own SSO). Swap
// that one function out; the scoping logic below it is the actual fix and
// doesn't need to change.

const express = require('express');
const jwt = require('jsonwebtoken');

const app = express();
app.use(express.json());

// In production this must come from an env var / secrets manager, never a
// literal in source — kept literal here only so this file runs standalone.
const JWT_SECRET = 'demo-secret-rotate-and-move-to-env-in-real-deployment';

// ---------------------------------------------------------------------------
// Server-side data. The client NEVER sees this array directly — only the
// slice a given request's verified token is entitled to.
// ---------------------------------------------------------------------------
const INTEGRATOR_NAME = 'Provita Agro Integrators';
const PORTFOLIO = (function buildPortfolio() {
  const segTypes = [
    { seg: 'Residential', n: 14, integrator: null },
    { seg: 'Commercial', n: 5, integrator: null },
    { seg: 'Poultry', n: 16, integrator: INTEGRATOR_NAME },
    { seg: 'Cold storage', n: 5, integrator: null },
  ];
  let id = 1000, rows = [];
  segTypes.forEach(group => {
    for (let i = 0; i < group.n; i++) {
      const genPerf = 70 + Math.random() * 30;
      const payRel = Math.min(100, Math.max(35, genPerf - 8 + (Math.random() * 24 - 12)));
      const composite = genPerf * 0.5 + payRel * 0.5;
      const tier = composite >= 88 ? 'Low' : composite >= 72 ? 'Medium' : 'High';
      rows.push({
        id: 'ST-' + (id++), segment: group.seg, integrator: group.integrator,
        genPerf, payRel, tier,
        value: group.seg === 'Cold storage' ? 24_800_000 : group.seg === 'Poultry' ? 470_000 : group.seg === 'Commercial' ? 800_000 : 350_000,
      });
    }
  });
  return rows;
})();

// ---------------------------------------------------------------------------
// STAND-IN for real credential verification — replace this function only.
// ---------------------------------------------------------------------------
function verifyCredentials(username, password) {
  const DEMO_USERS = {
    'bank-user': { password: 'demo', role: 'lender', integratorName: null },
    'provita-user': { password: 'demo', role: 'integrator', integratorName: INTEGRATOR_NAME },
  };
  const u = DEMO_USERS[username];
  if (!u || u.password !== password) return null;
  return { role: u.role, integratorName: u.integratorName };
}

app.post('/api/login', (req, res) => {
  const { username, password } = req.body || {};
  const identity = verifyCredentials(username, password);
  if (!identity) return res.status(401).json({ error: 'invalid credentials' });
  const token = jwt.sign(identity, JWT_SECRET, { expiresIn: '8h' });
  res.json({ token });
});

function requireAuth(req, res, next) {
  const header = req.headers.authorization || '';
  const token = header.startsWith('Bearer ') ? header.slice(7) : null;
  if (!token) return res.status(401).json({ error: 'missing bearer token' });
  try {
    req.auth = jwt.verify(token, JWT_SECRET);
    next();
  } catch {
    return res.status(401).json({ error: 'invalid or expired token' });
  }
}

// THE ACTUAL FIX: scoping decided from req.auth (server-verified), never
// from a query param, header, or anything else the client could set.
app.get('/api/portfolio', requireAuth, (req, res) => {
  const { role, integratorName } = req.auth;
  const rows = role === 'lender'
    ? PORTFOLIO
    : PORTFOLIO.filter(r => r.integrator === integratorName);

  res.json({
    scope: role === 'lender' ? 'all' : integratorName,
    count: rows.length,
    stats: {
      systemsInView: rows.length,
      financedValueTk: rows.reduce((a, r) => a + r.value, 0),
      avgRiskScore: rows.length ? rows.reduce((a, r) => a + (r.genPerf * 0.5 + r.payRel * 0.5), 0) / rows.length : 0,
      onTimePaymentRate: rows.length ? rows.reduce((a, r) => a + r.payRel, 0) / rows.length : 0,
    },
    rows: rows.map(r => ({ id: r.id, segment: r.segment, genPerf: r.genPerf, payRel: r.payRel, tier: r.tier })),
  });
});

const PORT = process.env.PORT || 3001;
if (require.main === module) {
  app.listen(PORT, () => console.log(`Portal backend listening on :${PORT}`));
}
module.exports = app;
