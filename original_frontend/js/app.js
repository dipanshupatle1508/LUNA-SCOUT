/* Luna Scout frontend logic. Backend endpoints: GET /api/sites, GET /api/timeline */
const $ = id => document.getElementById(id);
let sites = [];

/* ----- UI state ----- */
const showNote = () => {
  const s = sites.find(x => x.id === $('site').value);
  $('note').textContent = s ? `${s.status === 'landed' ? 'Landed' : 'Candidate'} · ${s.lat}°, ${s.lon}° · ${s.note}` : '';
};
const openMission = () => { document.body.classList.add('mission'); showNote(); };
$('start').onclick = openMission;
$('back').onclick = () => document.body.classList.remove('mission');
$('date').value = new Date(Date.now() + 30 * 864e5).toISOString().slice(0, 10);
$('site').onchange = showNote;

/* ----- Check site: call backend, show metrics + chart ----- */
$('run').onclick = async () => {
  $('msg').textContent = 'Computing…'; $('metrics').innerHTML = '';
  try {
    const q = new URLSearchParams({ site: $('site').value, start: $('date').value, days: $('days').value });
    const r = await fetch('/api/timeline?' + q);
    const d = await r.json();
    if (!r.ok) throw new Error(d.detail);
    const S = d.summary;
    $('msg').textContent = S.terrain_aware ? 'Terrain-aware horizon.' : 'Flat horizon only: add a terrain profile for real polar results.';
    const m = [[S.sunlit_hours + ' h', 'Sunlit'], [S.earth_hours + ' h', 'Earth in view'], [S.longest_dark_hours + ' h', 'Longest dark spell'], [S.max_sun_el + '°', 'Peak sun elevation']];
    $('metrics').innerHTML = m.map(([v, l]) => `<div><b>${v}</b><span>${l}</span></div>`).join('');
    draw(d);
  } catch (e) { $('msg').textContent = e.message; }
};

/* ----- Sun / Earth elevation chart (canvas) ----- */
function draw(d) {
  const c = $('chart'), k = devicePixelRatio, W = c.clientWidth, H = c.clientHeight;
  c.width = W * k; c.height = H * k;
  const g = c.getContext('2d'); g.scale(k, k);
  const n = d.t.length, y = v => H / 2 - (v / 30) * (H / 2 - 6), x = i => i / (n - 1) * W;
  g.strokeStyle = 'rgba(255,255,255,.2)'; g.beginPath(); g.moveTo(0, y(0)); g.lineTo(W, y(0)); g.stroke();
  [['sun_el', '#e8b86a'], ['earth_el', '#7fb3d5']].forEach(([key, col]) => {
    g.strokeStyle = col; g.lineWidth = 1.5; g.beginPath();
    d[key].forEach((v, i) => i ? g.lineTo(x(i), y(Math.max(-30, Math.min(30, v)))) : g.moveTo(0, y(v)));
    g.stroke();
  });
  g.fillStyle = '#8d9099'; g.font = '10px Inter,sans-serif'; g.fillText('horizon', 4, y(0) - 4);
}

/* ----- Load sites -> dropdown + chips ----- */
fetch('/api/sites').then(r => r.json()).then(s => {
  sites = s;
  $('site').innerHTML = s.map(x => `<option value="${x.id}">${x.name}</option>`).join('');
  $('chips').innerHTML = s.map(x => `<button class="chip glass ${x.status}" data-id="${x.id}">${x.name.split(' (')[0]}</button>`).join('');
  $('chips').onclick = e => { const b = e.target.closest('.chip'); if (b) { $('site').value = b.dataset.id; openMission(); } };
  showNote();
});
