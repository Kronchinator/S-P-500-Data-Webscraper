from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "processed" / "stockoracle_sector_dataset.json"
OUT_PATH = ROOT / "dashboard" / "index.html"

TEMPLATE = """<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>StockOracle Sector Dashboard</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
  <link href=\"https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap\" rel=\"stylesheet\">
  <style>
    :root {
      --bg:#07060e;
      --panel:#0f0e1c;
      --panel-2:#161527;
      --line:#231f3d;
      --line-2:#2e2a50;
      --text:#ede9ff;
      --muted:#7b74a8;
      --accent:#7c5cfc;
      --accent-dim:rgba(124,92,252,.12);
      --good:#1ed99a;
      --good-dim:rgba(30,217,154,.13);
      --warn:#f5b731;
      --warn-dim:rgba(245,183,49,.13);
      --bad:#ff5e7d;
      --bad-dim:rgba(255,94,125,.13);
    }
    * { box-sizing:border-box; }
    body {
      font-family: Inter, system-ui, sans-serif;
      background: var(--bg);
      background-image: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(124,92,252,.18) 0%, transparent 70%);
      color:var(--text);
      margin:0;
      padding:28px;
    }
    .wrap { max-width:1520px; margin:0 auto; }
    h1,h2,h3 { margin:0; }
    p { color:var(--muted); margin:0; }
    .hero {
      display:flex;
      justify-content:space-between;
      gap:16px;
      align-items:flex-end;
      margin-bottom:28px;
      flex-wrap:wrap;
      padding-bottom:20px;
      border-bottom:1px solid var(--line);
    }
    .hero-brand { display:flex; align-items:center; gap:14px; }
    .hero-icon {
      width:44px; height:44px;
      background: linear-gradient(135deg, #7c5cfc, #a855f7);
      border-radius:12px;
      display:flex; align-items:center; justify-content:center;
      font-size:22px;
      box-shadow: 0 0 24px rgba(124,92,252,.4);
      flex-shrink:0;
    }
    h1 {
      font-size:28px;
      font-weight:700;
      background: linear-gradient(90deg, #ede9ff 0%, #a78bfa 60%, #7c5cfc 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      letter-spacing: -0.02em;
    }
    .hero-sub { font-size:13px; color:var(--muted); margin-top:4px; }
    .record-badge {
      font-size:12px;
      font-family: 'JetBrains Mono', monospace;
      color:var(--accent);
      background:var(--accent-dim);
      border:1px solid rgba(124,92,252,.3);
      padding:6px 14px;
      border-radius:999px;
      white-space:nowrap;
    }
    .cards {
      display:grid;
      grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
      gap:12px;
      margin:0 0 24px;
    }
    .card {
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:16px;
      padding:18px 16px;
      box-shadow:0 4px 24px rgba(0,0,0,.35);
      position:relative;
      overflow:hidden;
      transition: border-color .15s;
    }
    .card::before {
      content:'';
      position:absolute;
      top:0; left:0; right:0;
      height:2px;
      background:linear-gradient(90deg,#7c5cfc,#a855f7);
      opacity:.6;
    }
    .card:hover { border-color:var(--line-2); }
    .section {
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:16px;
      padding:18px;
      box-shadow:0 4px 24px rgba(0,0,0,.3);
      margin:0;
    }
    .k { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.1em; font-weight:500; }
    .v { font-size:26px; font-weight:700; margin-top:8px; font-family:'JetBrains Mono',monospace; letter-spacing:-0.02em; }
    .toolbar {
      display:grid;
      grid-template-columns:2fr repeat(4,1fr) auto;
      gap:10px;
      margin-bottom:18px;
    }
    .input, select {
      width:100%;
      background:var(--panel);
      color:var(--text);
      border:1px solid var(--line);
      border-radius:10px;
      padding:10px 14px;
      outline:none;
      font-family:inherit;
      font-size:14px;
      transition:border-color .15s;
    }
    .input:focus, select:focus { border-color:var(--accent); }
    select option { background:var(--panel-2); }
    button {
      width:100%;
      background:linear-gradient(135deg,#7c5cfc,#a855f7);
      color:#fff;
      border:none;
      border-radius:10px;
      padding:10px 18px;
      font-weight:600;
      font-size:14px;
      font-family:inherit;
      cursor:pointer;
      transition:opacity .15s, box-shadow .15s;
      box-shadow:0 0 18px rgba(124,92,252,.3);
    }
    button:hover { opacity:.88; box-shadow:0 0 26px rgba(124,92,252,.5); }
    .panel {
      background:var(--panel);
      border:1px solid var(--line);
      border-radius:16px;
      overflow:hidden;
      box-shadow:0 4px 24px rgba(0,0,0,.3);
    }
    .table-wrap { overflow:auto; max-height:68vh; }
    table { width:100%; border-collapse:collapse; }
    th, td {
      padding:11px 12px;
      border-bottom:1px solid var(--line);
      text-align:left;
      font-size:13.5px;
      white-space:nowrap;
    }
    th {
      color:var(--muted);
      font-size:11px;
      font-weight:600;
      text-transform:uppercase;
      letter-spacing:.07em;
      position:sticky;
      top:0;
      background:rgba(13,12,24,.97);
      backdrop-filter:blur(10px);
      z-index:1;
      cursor:pointer;
      user-select:none;
      transition:color .15s;
    }
    th:hover { color:var(--text); }
    th[data-sort]::after { content:' ↕'; opacity:.35; font-size:10px; }
    tr:hover td { background:rgba(124,92,252,.04); }
    td:first-child, td:nth-child(4), td:nth-child(5), td:nth-child(6) {
      font-family:'JetBrains Mono',monospace;
      font-size:13px;
    }
    .pill {
      display:inline-block;
      padding:3px 10px;
      border-radius:999px;
      font-size:11px;
      font-weight:700;
      letter-spacing:.04em;
    }
    .HIGH,.WIDE,.UNDERVALUED,.GOOD { background:var(--good-dim); color:var(--good); border:1px solid rgba(30,217,154,.2); }
    .MEDIUM,.FAIRLY_VALUED,.NARROW { background:var(--warn-dim); color:var(--warn); border:1px solid rgba(245,183,49,.2); }
    .LOW,.OVERVALUED,.NO_MOAT,.WEAK { background:var(--bad-dim); color:var(--bad); border:1px solid rgba(255,94,125,.2); }
    .sub { font-size:12px; color:var(--muted); margin-top:4px; }
    .grid-2 { display:grid; grid-template-columns:1.25fr 1fr; gap:14px; margin:18px 0; }
    .section h3 { font-size:15px; font-weight:600; margin-bottom:4px; }
    .mini-table td, .mini-table th { padding:9px 10px; font-size:13px; }
    .legend { display:flex; flex-wrap:wrap; gap:10px; margin-top:14px; align-items:center; }
    .legend-item { display:flex; align-items:center; gap:6px; font-size:12px; color:var(--muted); }
    .footer-note { margin-top:12px; font-size:11.5px; color:var(--muted); font-family:'JetBrains Mono',monospace; }
    @media (max-width: 1100px) { .grid-2 { grid-template-columns:1fr; } }
    @media (max-width: 980px) { .toolbar { grid-template-columns:1fr 1fr; } }
    @media (max-width: 640px) { .toolbar { grid-template-columns:1fr; } body { padding:14px; } h1 { font-size:22px; } }
  </style>
</head>
<body>
<div class=\"wrap\">
  <div class=\"hero\">
    <div class=\"hero-brand\">
      <div class=\"hero-icon\">◎</div>
      <div>
        <h1>StockOracle Sector Dashboard</h1>
        <div class=\"hero-sub\">SPDR sector ETF holdings enriched with PAGI6 ranks and intrinsic-value endpoints</div>
      </div>
    </div>
    <div class=\"record-badge\">__COUNT__ tickers loaded</div>
  </div>

  <div class=\"cards\" id=\"summaryCards\"></div>

  <div class=\"toolbar\">
    <input id=\"search\" class=\"input\" placeholder=\"Search ticker or company name\">
    <select id=\"etfFilter\"></select>
    <select id=\"moatFilter\"></select>
    <select id=\"profitFilter\"></select>
    <select id=\"valuationFilter\"></select>
    <button id=\"exportBtn\">Export CSV</button>
  </div>

  <div class=\"grid-2\">
    <div class=\"section\">
      <h3>Top opportunities</h3>
      <p class=\"sub\">Highest DCF upside among currently visible stocks.</p>
      <div class=\"table-wrap\">
        <table class=\"mini-table\">
          <thead>
            <tr><th>Ticker</th><th>Name</th><th>DCF Upside</th><th>Moat</th><th>Valuation</th></tr>
          </thead>
          <tbody id=\"topRows\"></tbody>
        </table>
      </div>
    </div>
    <div class=\"section\">
      <h3>ETF drilldown</h3>
      <p class=\"sub\">Quick sector summary based on the current filter state.</p>
      <div class=\"table-wrap\">
        <table class=\"mini-table\">
          <thead>
            <tr><th>ETF</th><th>Stocks</th><th>Avg Upside</th><th>Wide Moat</th><th>Undervalued</th></tr>
          </thead>
          <tbody id=\"etfRows\"></tbody>
        </table>
      </div>
    </div>
  </div>

  <div class=\"panel\">
    <div class=\"table-wrap\">
      <table>
        <thead>
          <tr>
            <th data-sort=\"ticker\">Ticker</th>
            <th data-sort=\"name\">Name</th>
            <th data-sort=\"etfs\">ETFs</th>
            <th data-sort=\"oracle_value\">Oracle Value</th>
            <th data-sort=\"dcf_value\">DCF Value</th>
            <th data-sort=\"upside\">DCF Upside %</th>
            <th data-sort=\"profitability\">Profitability</th>
            <th data-sort=\"financial_strength\">Financial Strength</th>
            <th data-sort=\"oracle_moat\">Oracle Moat</th>
            <th data-sort=\"valuation\">Valuation</th>
          </tr>
        </thead>
        <tbody id=\"rows\"></tbody>
      </table>
    </div>
  </div>

  <div class=\"section\">
    <h3>Legend</h3>
    <div class=\"legend\">
      <div class=\"legend-item\"><span class=\"pill HIGH\">HIGH</span> stronger quality signal</div>
      <div class=\"legend-item\"><span class=\"pill MEDIUM\">MEDIUM</span> mixed / decent</div>
      <div class=\"legend-item\"><span class=\"pill LOW\">LOW</span> weaker signal</div>
      <div class=\"legend-item\"><span class=\"pill WIDE\">WIDE</span> strongest moat bucket</div>
      <div class=\"legend-item\"><span class=\"pill UNDERVALUED\">UNDERVALUED</span> attractive relative value</div>
      <div class=\"legend-item\"><span class=\"pill OVERVALUED\">OVERVALUED</span> richer pricing</div>
    </div>
    <div class=\"footer-note\">// DCF upside = (DCF Value − Oracle Value) / Oracle Value</div>
  </div>
</div>
<script>
const rawData = __DATA__.map(r => {
  const oracle = Number(r.oracle_value);
  const dcf = Number(r.dcf_value);
  return { ...r, oracle_value_num: oracle, dcf_value_num: dcf, upside: oracle ? (((dcf - oracle) / oracle) * 100) : null };
});
let currentSort = { key: 'upside', dir: 'desc' };

function uniqueValues(key) {
  return [...new Set(rawData.map(r => r[key]).filter(Boolean))].sort();
}

function pillClass(value) {
  return String(value || '').replace(/\\s+/g, '_').replace(/[^A-Za-z0-9_]/g, '').toUpperCase();
}

function formatNum(value) {
  if (value === null || value === undefined || value === '' || Number.isNaN(Number(value))) return '';
  return Number(value).toFixed(2);
}

function formatPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '';
  return Number(value).toFixed(1) + '%';
}

function makeOptions(id, values, label) {
  const el = document.getElementById(id);
  el.innerHTML = `<option value="">All ${label}</option>` + values.map(v => `<option value="${v}">${v}</option>`).join('');
}

function filteredData() {
  const q = document.getElementById('search').value.trim().toLowerCase();
  const etf = document.getElementById('etfFilter').value;
  const moat = document.getElementById('moatFilter').value;
  const profit = document.getElementById('profitFilter').value;
  const valuation = document.getElementById('valuationFilter').value;
  return rawData.filter(r => {
    if (q && !(r.ticker.toLowerCase().includes(q) || r.name.toLowerCase().includes(q))) return false;
    if (etf && !r.etfs.split(',').map(x => x.trim()).includes(etf)) return false;
    if (moat && r.oracle_moat !== moat) return false;
    if (profit && r.profitability !== profit) return false;
    if (valuation && r.valuation !== valuation) return false;
    return true;
  });
}

function sortData(data) {
  const arr = [...data];
  const { key, dir } = currentSort;
  arr.sort((a,b) => {
    const av = a[key + '_num'] ?? a[key] ?? '';
    const bv = b[key + '_num'] ?? b[key] ?? '';
    const cmp = typeof av === 'number' && typeof bv === 'number' ? av - bv : String(av).localeCompare(String(bv));
    return dir === 'asc' ? cmp : -cmp;
  });
  return arr;
}

function renderCards(data) {
  const avgUpside = data.length ? data.reduce((s,r) => s + (r.upside || 0), 0) / data.length : 0;
  const wide = data.filter(r => r.oracle_moat === 'WIDE').length;
  const undervalued = data.filter(r => r.valuation === 'UNDERVALUED').length;
  const highProfit = data.filter(r => r.profitability === 'HIGH').length;
  const highStrength = data.filter(r => r.financial_strength === 'HIGH').length;
  document.getElementById('summaryCards').innerHTML = `
    <div class="card"><div class="k">Visible stocks</div><div class="v">${data.length}</div></div>
    <div class="card"><div class="k">Avg DCF upside</div><div class="v">${formatPct(avgUpside)}</div></div>
    <div class="card"><div class="k">Wide moat</div><div class="v">${wide}</div></div>
    <div class="card"><div class="k">Undervalued</div><div class="v">${undervalued}</div></div>
    <div class="card"><div class="k">High profitability</div><div class="v">${highProfit}</div></div>
    <div class="card"><div class="k">High financial strength</div><div class="v">${highStrength}</div></div>
  `;
}

function renderTopRows(data) {
  const top = [...data].filter(r => r.upside !== null).sort((a,b) => b.upside - a.upside).slice(0, 12);
  document.getElementById('topRows').innerHTML = top.map(r => `
    <tr>
      <td><strong>${r.ticker}</strong></td>
      <td>${r.name}</td>
      <td>${formatPct(r.upside)}</td>
      <td><span class="pill ${pillClass(r.oracle_moat)}">${r.oracle_moat || ''}</span></td>
      <td><span class="pill ${pillClass(r.valuation)}">${r.valuation || ''}</span></td>
    </tr>
  `).join('');
}

function renderEtfRows(data) {
  const groups = {};
  for (const row of data) {
    for (const etf of row.etfs.split(',').map(x => x.trim()).filter(Boolean)) {
      groups[etf] ||= [];
      groups[etf].push(row);
    }
  }
  const etfs = Object.entries(groups).sort((a,b) => a[0].localeCompare(b[0]));
  document.getElementById('etfRows').innerHTML = etfs.map(([etf, rows]) => {
    const avgUpside = rows.length ? rows.reduce((s,r) => s + (r.upside || 0), 0) / rows.length : 0;
    const wide = rows.filter(r => r.oracle_moat === 'WIDE').length;
    const undervalued = rows.filter(r => r.valuation === 'UNDERVALUED').length;
    return `
      <tr>
        <td><strong>${etf}</strong></td>
        <td>${rows.length}</td>
        <td>${formatPct(avgUpside)}</td>
        <td>${wide}</td>
        <td>${undervalued}</td>
      </tr>
    `;
  }).join('');
}

function renderTable() {
  const data = sortData(filteredData());
  renderCards(data);
  renderTopRows(data);
  renderEtfRows(data);
  document.getElementById('rows').innerHTML = data.map(r => `
    <tr>
      <td><strong>${r.ticker}</strong></td>
      <td>${r.name}</td>
      <td>${r.etfs}</td>
      <td>${formatNum(r.oracle_value)}</td>
      <td>${formatNum(r.dcf_value)}</td>
      <td>${formatPct(r.upside)}</td>
      <td><span class="pill ${pillClass(r.profitability)}">${r.profitability || ''}</span></td>
      <td><span class="pill ${pillClass(r.financial_strength)}">${r.financial_strength || ''}</span></td>
      <td><span class="pill ${pillClass(r.oracle_moat)}">${r.oracle_moat || ''}</span></td>
      <td><span class="pill ${pillClass(r.valuation)}">${r.valuation || ''}</span></td>
    </tr>
  `).join('');
}

function exportCsv() {
  const rows = filteredData();
  const headers = ['ticker','name','etfs','oracle_value','dcf_value','upside','profitability','financial_strength','oracle_moat','valuation'];
  const lines = [headers.join(',')].concat(rows.map(r => headers.map(h => JSON.stringify(r[h] ?? '')).join(',')));
  const blob = new Blob([lines.join('\\n')], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'stockoracle-filtered-export.csv';
  a.click();
  URL.revokeObjectURL(url);
}

makeOptions('etfFilter', [...new Set(rawData.flatMap(r => r.etfs.split(',').map(x => x.trim())).filter(Boolean))].sort(), 'ETF');
makeOptions('moatFilter', uniqueValues('oracle_moat'), 'Moat');
makeOptions('profitFilter', uniqueValues('profitability'), 'Profitability');
makeOptions('valuationFilter', uniqueValues('valuation'), 'Valuation');

for (const id of ['search','etfFilter','moatFilter','profitFilter','valuationFilter']) {
  document.getElementById(id).addEventListener('input', renderTable);
  document.getElementById(id).addEventListener('change', renderTable);
}

document.getElementById('exportBtn').addEventListener('click', exportCsv);

document.querySelectorAll('th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    currentSort = currentSort.key === key ? { key, dir: currentSort.dir === 'asc' ? 'desc' : 'asc' } : { key, dir: 'desc' };
    renderTable();
  });
});

renderTable();
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads(DATA_PATH.read_text())
    html = TEMPLATE.replace("__DATA__", json.dumps(data)).replace("__COUNT__", str(len(data)))
    OUT_PATH.write_text(html)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
