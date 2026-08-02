// DROP-IN REPLACEMENT for the PORTFOLIO/renderPortal section of
// solarthik-platform-prototype.html, once portal-server.js (or a real
// equivalent) is deployed somewhere the page can reach.
//
// DELETE from the HTML file: the entire `let PORTFOLIO = [...]` array and
// the `(function buildPortfolio(){...})()` IIFE that fills it. The client
// should never construct or hold the full portfolio again — that data lives
// only on the server now.

let authToken = null; // set once after login; kept in memory only for the session

async function login(username, password) {
  const res = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('login failed');
  const { token } = await res.json();
  authToken = token;
}

let portalView = 'lender';
let riskChart = null;

async function renderPortal() {
  if (!authToken) {
    document.getElementById('portTableBody').innerHTML = '<tr><td colspan="5">Not signed in.</td></tr>';
    return;
  }

  const res = await fetch('/api/portfolio', { headers: { Authorization: `Bearer ${authToken}` } });
  if (res.status === 401) {
    authToken = null;
    document.getElementById('portTableBody').innerHTML = '<tr><td colspan="5">Session expired — please sign in again.</td></tr>';
    return;
  }
  const data = await res.json();

  document.getElementById('statCount').textContent = data.count;
  document.getElementById('statValue').textContent = 'Tk ' + (data.stats.financedValueTk / 1e6).toFixed(1) + 'M';
  document.getElementById('statRisk').textContent = data.stats.avgRiskScore.toFixed(0) + '/100';
  document.getElementById('statPayRate').textContent = data.stats.onTimePaymentRate.toFixed(0) + '%';

  document.getElementById('portTableBody').innerHTML = data.rows.slice(0, 60).map(r =>
    `<tr><td class="id">${r.id}</td><td>${r.segment}</td><td>${r.genPerf.toFixed(0)}%</td><td>${r.payRel.toFixed(0)}%</td><td><span class="tier-badge ${r.tier}">${r.tier}</span></td></tr>`
  ).join('');

  const ctx = document.getElementById('riskChart').getContext('2d');
  const chartData = {
    datasets: [{
      label: 'Systems',
      data: data.rows.map(r => ({ x: r.genPerf, y: r.payRel })),
      backgroundColor: data.rows.map(r => r.tier === 'Low' ? 'rgba(95,180,137,.75)' : r.tier === 'Medium' ? 'rgba(231,169,62,.75)' : 'rgba(226,96,79,.75)'),
      pointRadius: 5,
    }],
  };
  const options = {
    responsive: true, maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { callbacks: { label: (c) => `Gen ${c.parsed.x.toFixed(0)}% / Pay ${c.parsed.y.toFixed(0)}%` } } },
    scales: {
      x: { title: { display: true, text: 'Generation vs projection (%)', color: '#93A0BC' }, ticks: { color: '#93A0BC' }, grid: { color: 'rgba(255,255,255,.06)' } },
      y: { title: { display: true, text: 'On-time payment rate (%)', color: '#93A0BC' }, ticks: { color: '#93A0BC' }, grid: { color: 'rgba(255,255,255,.06)' } },
    },
  };
  if (riskChart) { riskChart.data = chartData; riskChart.options = options; riskChart.update(); }
  else { riskChart = new Chart(ctx, { type: 'scatter', data: chartData, options }); }
}

document.querySelectorAll('#portalSeg .seg-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    document.querySelectorAll('#portalSeg .seg-btn').forEach(b => b.classList.toggle('is-active', b === btn));
    portalView = btn.dataset.view;
    await login(portalView === 'lender' ? 'bank-user' : 'provita-user', 'demo');
    renderPortal();
  });
});
