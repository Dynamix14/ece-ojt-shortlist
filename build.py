#!/usr/bin/env python3
"""Builds index.html for the ECE OJT shortlist (v2) from data.json."""
import html, json, pathlib

HERE = pathlib.Path(__file__).parent
ROWS = json.loads((HERE / "data.json").read_text(encoding="utf-8"))
BENCH = ("Indeed puts the Philippine engineering intern at ₱15,307/mo on average "
         "(₱18,255 in Manila) — but that is 3 reported salaries, so treat it as a sniff test, not a rate card.")


def esc(s):
    return html.escape(str(s), quote=True)


def fit_badge(fit):
    cls = "b-high" if fit in ("HIGH", "MED-HIGH") else "b-mid" if fit == "MEDIUM" else "b-low"
    label = {"HIGH": "strong ECE fit", "MED-HIGH": "good ECE fit",
             "MEDIUM": "partial fit", "LOW-MED": "thin fit", "LOW": "weak fit"}[fit]
    return f'<span class="badge {cls}">{label}</span>'


def money_badge(m):
    cls = {"amount": "m-yes", "hint": "m-soft", "none": "m-no"}[m["tier"]]
    label = {"amount": "figure published", "hint": "mentioned, no figure", "none": "nothing published"}[m["tier"]]
    return f'<span class="badge {cls}">{label}</span>'


def money_block(m):
    cls = {"amount": "amount", "hint": "hint", "none": "none"}[m["tier"]]
    src = f'<a href="{esc(m["src"])}" target="_blank" rel="noopener">source</a>' if m["src"] else ""
    return f"""<div class="money {cls}">
      <div class="m-top"><span class="m-label">expected allowance</span>{src}</div>
      <div class="m-amount">{esc(m['amount'])}</div>
      <p class="m-basis">{esc(m['basis'])}</p>
      <p class="m-note">{esc(m['note'])}</p>
    </div>"""


def row(idx, r):
    roles = "".join(f"<li>{esc(x.strip())}</li>" for x in r["roles"].split(";") if x.strip())
    links = [f'<a href="{esc(r["site"])}" target="_blank" rel="noopener">website</a>']
    if r["linkedin"]:
        links.append(f'<a href="{esc(r["linkedin"])}" target="_blank" rel="noopener">LinkedIn</a>')
    links.append(f'<a href="{esc(r["careers"])}" target="_blank" rel="noopener">careers</a>')
    for t, u in r["posts"]:
        links.append(f'<a class="post" href="{esc(u)}" target="_blank" rel="noopener">{esc(t.split("—")[0].split("(")[0].strip())}</a>')

    it = r["intern"]
    if it["n"]:
        bl = "".join(f"<li>{esc(b)}</li>" for b in it["bullets"][:3])
        quote = f'<blockquote>{esc(it["quote"])}</blockquote>' if it["quote"] else ""
        src = f'<a href="{esc(it["url"])}" target="_blank" rel="noopener">source</a>' if it["url"] else ""
        reality = f"""<div class="reality">
          <div class="r-head"><span class="r-tag">intern reality</span><span class="r-stars">{esc(it['stars'])} / 5</span>
          <span class="r-src">{esc(it['src'])}</span>{src}</div>
          <ul class="r-list">{bl}</ul>{quote}</div>"""
    else:
        bl = "".join(f"<li>{esc(b)}</li>" for b in it["bullets"][:2])
        reality = f"""<div class="reality none">
          <div class="r-head"><span class="r-tag muted">intern reality</span>
          <span class="r-src">no first-hand account found — duties are inferred</span></div>
          <ul class="r-list">{bl}</ul></div>"""

    slots = r["slots"] if not r["slots"].startswith("http") else "⚠ data error in masterlist (Alstom careers URL)"
    panel = f"""<div class="panel">
      <dl class="kv"><dt>Address</dt><dd>{esc(r['address'])}</dd></dl>
      <dl class="kv"><dt>Contact</dt><dd>{esc(r['contact'])}<br><span style="color:var(--muted)">{esc(r['position'])}</span></dd></dl>
      <dl class="kv"><dt>Email</dt><dd><a href="mailto:{esc(r['email'].split('|')[0].split('/')[0].strip())}">{esc(r['email'])}</a></dd></dl>
      <dl class="kv"><dt>MOA</dt><dd>{esc(r['effectivity'])}</dd></dl>
      <dl class="kv"><dt>Slots</dt><dd>{esc(slots or 'not stated')}</dd></dl>
      <dl class="kv"><dt>Intake</dt><dd>{esc(r['intake'] or 'not stated')}</dd></dl>
    </div>"""
    txt = " ".join([r["name_short"], r["roles"], r["offering"], r["address"],
                    r["money"]["amount"], r["money"]["basis"], " ".join(it["bullets"])]).lower()
    return f"""  <li class="row" data-km="{r['km']}" data-fit="{r['fit']}" data-money="{r['money']['tier']}" data-text="{esc(txt)}">
    <div class="rank">{idx:02d}</div>
    <div class="body">
      <div class="head">
        <h2>{esc(r['name_short'])}</h2>
        {fit_badge(r['fit'])}
        <span class="dist"><span class="bar" aria-hidden="true"><i class="{'far' if r['km']>10 else ''}" style="width:{min(100,max(6,(r['km']/22)**0.5*100)):.0f}%"></i></span>{r['km']:g} km · ~{r['min']} min</span>
      </div>
      {money_block(r['money'])}
      <ul class="roles">{roles}</ul>
      <p class="what"><b>what they do</b>{esc(r['offering'])}</p>
      {reality}
      <div class="links">{''.join(links)}</div>
      <details class="more"><summary>contact &amp; MOA details</summary>{panel}</details>
    </div>
  </li>"""


def table_row(r):
    m = r["money"]
    cls = {"amount": "amount", "hint": "hint", "none": "none"}[m["tier"]]
    return f"""<tr class="{cls}">
      <td class="t-name">{esc(r['name_short'])}</td>
      <td class="t-money">{esc(m['amount'])}</td>
      <td class="t-km">{r['km']:g} km</td>
      <td class="t-note">{esc(m['basis'][:110])}{'…' if len(m['basis'])>110 else ''}</td>
    </tr>"""


CSS = """
  :root{
    --ink:#141a1f; --ink-2:#3d4a52; --muted:#6b7a82;
    --paper:#f7f4ee; --surface:#fffdf9; --line:#ddd6c9; --line-soft:#e9e3d8;
    --accent:#a8331f; --accent-soft:#f4e3dd;
    --ok:#1f5c3d; --ok-soft:#e2efe6;
    --warn:#8a5a00; --warn-soft:#f7ecd7;
    --radius:3px; --max:1060px;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
    --serif:"Iowan Old Style","Palatino Linotype",Palatino,Georgia,"Times New Roman",serif;
    --mono:ui-monospace,"SF Mono","Cascadia Mono",Menlo,Consolas,monospace;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
  a{color:var(--accent);text-decoration:none;text-underline-offset:2px}
  a:hover{text-decoration:underline}
  a:focus-visible,button:focus-visible,input:focus-visible,summary:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
  .wrap{max-width:var(--max);margin:0 auto;padding:0 20px}
  header.mast{border-bottom:2px solid var(--ink)}
  .mast-inner{display:flex;flex-wrap:wrap;gap:16px;align-items:flex-end;justify-content:space-between;padding:26px 20px 16px;max-width:var(--max);margin:0 auto}
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
  h1{font-family:var(--serif);font-weight:600;font-size:clamp(29px,4.6vw,44px);line-height:1.06;margin:6px 0 8px;letter-spacing:-.01em}
  .dek{max-width:58ch;color:var(--ink-2);font-size:15px;margin:0}
  .stamp{font-family:var(--mono);font-size:11px;color:var(--muted);text-align:right;line-height:1.7;white-space:nowrap}
  .controls{position:sticky;top:0;z-index:20;background:rgba(247,244,238,.95);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);padding:11px 0}
  .controls-inner{display:flex;flex-wrap:wrap;gap:10px 14px;align-items:center;max-width:var(--max);margin:0 auto;padding:0 20px}
  .filters{display:flex;flex-wrap:wrap;gap:6px}
  .chip{font:inherit;font-size:13px;padding:5px 11px;background:transparent;border:1px solid var(--line);color:var(--ink-2);border-radius:999px;cursor:pointer;transition:background .15s,border-color .15s,color .15s}
  .chip:hover{border-color:var(--ink-2)}
  .chip[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--paper)}
  .search{margin-left:auto;display:flex;align-items:center;gap:8px}
  .search input{font:inherit;font-size:14px;padding:7px 10px;width:190px;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface);color:var(--ink)}
  .count{font-family:var(--mono);font-size:11px;color:var(--muted);letter-spacing:.06em;text-transform:uppercase}
  main{padding:24px 0 8px}
  .lead p{margin:0 0 12px;font-size:14.5px;color:var(--ink-2);max-width:78ch}
  .lead strong{color:var(--ink)}
  .bench{font-size:12.5px;color:var(--muted);border-left:2px solid var(--line);padding-left:10px;margin:0 0 22px;max-width:78ch}
  h2.sec{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 8px;font-weight:600}
  table.money-table{width:100%;border-collapse:collapse;margin:0 0 26px;font-size:14px}
  table.money-table th{text-align:left;font-family:var(--mono);font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);font-weight:600;padding:0 10px 6px 0;border-bottom:1px solid var(--ink)}
  table.money-table td{padding:9px 10px 9px 0;border-bottom:1px solid var(--line);vertical-align:top}
  tr.amount .t-money{color:var(--ok);font-weight:600}
  tr.hint .t-money{color:var(--warn);font-weight:600}
  tr.none .t-money{color:var(--muted)}
  .t-name{font-weight:600;white-space:nowrap}
  .t-money{white-space:nowrap;font-variant-numeric:tabular-nums}
  .t-km{font-family:var(--mono);font-size:12px;color:var(--ink-2);white-space:nowrap}
  .t-note{color:var(--muted);font-size:12.5px}
  ol.list{list-style:none;margin:0;padding:0;border-top:1px solid var(--line)}
  li.row{display:grid;grid-template-columns:44px 1fr;gap:0 18px;padding:20px 0 22px;border-bottom:1px solid var(--line)}
  .rank{font-family:var(--mono);font-size:13px;color:var(--muted);padding-top:3px;text-align:right}
  .body{min-width:0}
  .head{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 12px;margin-bottom:10px}
  h2{font-family:var(--serif);font-size:21px;font-weight:600;margin:0;line-height:1.25}
  .badge{font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;padding:2px 7px;border-radius:2px;white-space:nowrap}
  .b-high{background:var(--ok-soft);color:var(--ok)}
  .b-mid{background:var(--warn-soft);color:var(--warn)}
  .b-low{background:#ecebe6;color:var(--muted)}
  .m-yes{background:var(--ok-soft);color:var(--ok)}
  .m-soft{background:var(--warn-soft);color:var(--warn)}
  .m-no{background:#ecebe6;color:var(--muted)}
  .dist{margin-left:auto;display:flex;align-items:center;gap:9px;font-family:var(--mono);font-size:12px;color:var(--ink-2);white-space:nowrap}
  .bar{width:70px;height:4px;background:var(--line-soft);border-radius:2px;overflow:hidden;display:inline-block}
  .bar i{display:block;height:100%;background:var(--accent);border-radius:2px}
  .bar i.far{background:var(--muted)}
  .money{border:1px solid var(--line);border-radius:var(--radius);padding:10px 13px 11px;background:var(--surface);margin:0 0 12px}
  .money.amount{border-left:3px solid var(--ok)}
  .money.hint{border-left:3px solid var(--warn)}
  .money.none{border-left:3px solid var(--line)}
  .m-top{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
  .m-label{font-family:var(--mono);font-size:10px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
  .m-top a{font-size:11.5px}
  .m-amount{font-family:var(--serif);font-size:24px;line-height:1.2;margin:2px 0 4px;letter-spacing:-.01em}
  .money.amount .m-amount{color:var(--ok)}
  .money.none .m-amount{color:var(--muted);font-size:19px}
  .m-basis{margin:0;font-size:12.5px;color:var(--ink-2)}
  .m-note{margin:5px 0 0;font-size:12.5px;color:var(--muted)}
  .roles{margin:12px 0 0;padding:0;list-style:none;display:grid;gap:3px}
  .roles li{position:relative;padding-left:15px;font-size:14px}
  .roles li::before{content:"";position:absolute;left:2px;top:9px;width:5px;height:5px;background:var(--accent);border-radius:50%;opacity:.6}
  .what{font-size:13px;color:var(--ink-2);margin:9px 0 0;max-width:74ch}
  .what b{color:var(--muted);font-weight:600;font-family:var(--mono);font-size:10px;letter-spacing:.08em;text-transform:uppercase;margin-right:6px}
  .reality{margin:12px 0 0;padding:10px 13px 11px;background:var(--surface);border:1px solid var(--line-soft);border-left:2px solid var(--ok);border-radius:var(--radius)}
  .reality.none{border-left-color:var(--line);background:transparent}
  .r-head{display:flex;flex-wrap:wrap;align-items:baseline;gap:9px;margin-bottom:6px}
  .r-tag{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--ok)}
  .r-tag.muted{color:var(--muted)}
  .r-stars{font-family:var(--mono);font-size:11px;background:var(--ok-soft);color:var(--ink);padding:1px 6px;border-radius:2px}
  .r-src{font-size:11.5px;color:var(--muted)}
  .r-head a{font-size:11.5px}
  .r-list{margin:0;padding:0;list-style:none;display:grid;gap:3px}
  .r-list li{position:relative;padding-left:14px;font-size:13px;color:var(--ink-2)}
  .r-list li::before{content:"—";position:absolute;left:0;color:var(--muted);font-size:12px}
  blockquote{margin:8px 0 0;padding-left:11px;border-left:2px solid var(--line);font-size:12.5px;font-style:italic;color:var(--ink-2)}
  .links{display:flex;flex-wrap:wrap;gap:6px 14px;margin-top:11px;font-size:13px}
  .links a::after{content:"\\2197";font-size:10px;opacity:.55;margin-left:3px}
  .links .post{color:var(--ok);font-weight:600}
  .links .post::after{content:"\\2713";opacity:.7}
  details.more{margin-top:9px}
  details.more summary{cursor:pointer;color:var(--muted);font-family:var(--mono);font-size:10.5px;letter-spacing:.08em;text-transform:uppercase;list-style:none;display:inline-flex;gap:6px;align-items:center}
  details.more summary::-webkit-details-marker{display:none}
  details.more summary::before{content:"+";font-size:13px;color:var(--accent)}
  details.more[open] summary::before{content:"\\2212"}
  .panel{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:4px 22px;margin-top:8px;padding:10px 12px;background:var(--surface);border:1px solid var(--line-soft);border-radius:var(--radius)}
  .kv{display:grid;grid-template-columns:74px 1fr;gap:2px 8px;font-size:12.5px;padding:2px 0;margin:0}
  .kv dt{color:var(--muted);font-family:var(--mono);font-size:10px;letter-spacing:.06em;text-transform:uppercase;padding-top:2px}
  .kv dd{margin:0;min-width:0;overflow-wrap:anywhere}
  .empty{padding:36px 0;color:var(--muted);font-family:var(--mono);font-size:13px}
  footer{border-top:2px solid var(--ink);margin-top:28px;padding:24px 0 44px}
  footer h3{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);margin:0 0 9px}
  footer li,footer p{font-size:12.5px;color:var(--ink-2);max-width:80ch}
  footer ul{padding-left:18px;margin:0 0 16px}
  footer li{margin-bottom:5px}
  .cols{display:grid;gap:24px;grid-template-columns:1fr 1fr}
  @media (max-width:720px){
    .cols{grid-template-columns:1fr}
    .stamp{text-align:left}
    li.row{grid-template-columns:28px 1fr;gap:0 10px}
    .dist{margin-left:0;order:9;width:100%}
    .search{margin-left:0;width:100%}
    .search input{width:100%}
    .t-note{display:none}
    .m-amount{font-size:21px}
  }
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
"""

body_rows = "\n".join(row(i, r) for i, r in enumerate(ROWS, 1))
table = "\n".join(table_row(r) for r in ROWS)

HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ECE OJT shortlist — stipends & drive times from Taft</title>
<meta name="description" content="Seven face-to-face OJT companies that list ECE, ranked by driving distance from Taft, Malate, with the internship allowance each one actually pays.">
<style>{CSS}</style>
</head>
<body>
<header class="mast">
  <div class="mast-inner">
    <div>
      <div class="eyebrow">Mapúa ECE · v2 · the shortlist</div>
      <h1>Seven ECE targets,<br>and what each one pays</h1>
      <p class="dek">Narrowed to the companies you'd actually take. Ranked by drive time from DLSU–Taft, with the internship allowance traced to a posting, a review or a public statement — and marked <em>not published</em> where nobody has ever said.</p>
    </div>
    <div class="stamp">
      2 with a ₱ figure<br>
      2 with a hint only<br>
      3 with nothing<br>
      checked 7 Nov 2026
    </div>
  </div>
</header>

<div class="controls">
  <div class="controls-inner">
    <div class="filters" role="group" aria-label="Filter companies">
      <button class="chip" data-filter="all" aria-pressed="true">All 7</button>
      <button class="chip" data-filter="cash" aria-pressed="false">Has a ₱ figure</button>
      <button class="chip" data-filter="silent" aria-pressed="false">Nothing published</button>
      <button class="chip" data-filter="near" aria-pressed="false">≤ 6 km</button>
      <button class="chip" data-filter="high" aria-pressed="false">Strong ECE fit</button>
    </div>
    <div class="search">
      <label for="q" class="count">search</label>
      <input id="q" type="search" placeholder="stipend, RF, ELV, BGC…" autocomplete="off">
    </div>
  </div>
</div>

<main class="wrap">
  <div class="lead">
    <p><strong>Read the money column first.</strong> Only <strong>Security Bank</strong> and <strong>Coca-Cola EP</strong> publish an allowance. Meralco and Lattice allude to one without a number. APMC, Meinhardt and Edgepoint have never stated one — for those, assume unpaid until HR puts it in writing.</p>
    <p class="bench">{esc(BENCH)}</p>
  </div>

  <h2 class="sec">Allowance at a glance</h2>
  <table class="money-table">
    <thead><tr><th>Company</th><th>Allowance</th><th>Distance</th><th>Basis</th></tr></thead>
    <tbody>{table}</tbody>
  </table>

  <h2 class="sec">The seven, in detail</h2>
  <ol class="list">
{body_rows}
  </ol>
  <p class="empty" id="empty" hidden>Nothing matches that filter. Clear the search or pick “All 7”.</p>
</main>

<footer>
  <div class="wrap cols">
    <div>
      <h3>Where the numbers come from</h3>
      <ul>
        <li><b>₱ figures</b> are lifted from the posting itself — Prosple's salary field for Security Bank STAR, an Indeed salary line for the Coca-Cola Santa Rosa IE intern. Not estimates I invented.</li>
        <li><b>Distance</b> is OSRM road distance from DLSU–Taft (14.5649, 120.9931), traffic-free. Add 40–100% at rush hour.</li>
        <li><b>Intern reality</b> quotes Indeed and JobStreet intern reviews. “No first-hand account” means exactly that.</li>
        <li>Allowances shift per cohort and per business unit — the number in a 2025 posting is not a promise for 2027.</li>
      </ul>
    </div>
    <div>
      <h3>Ask these three questions</h3>
      <ul>
        <li>Is there a monthly allowance, and is it released weekly or at the end?</li>
        <li>Does it cover transport for site/plant visits, or is that separate?</li>
        <li>Which unit will I be assigned to? At Security Bank and Coca-Cola the answer changes the work entirely.</li>
      </ul>
    </div>
  </div>
</footer>
<script>
(function(){{
  const rows=[...document.querySelectorAll('li.row')];
  const chips=[...document.querySelectorAll('.chip[data-filter]')];
  const q=document.getElementById('q'), empty=document.getElementById('empty'), live=document.getElementById('live');
  let filter='all';
  function apply(){{
    const term=q.value.trim().toLowerCase(); let shown=0;
    rows.forEach(li=>{{
      const km=parseFloat(li.dataset.km), m=li.dataset.money, fit=li.dataset.fit;
      const ok = filter==='all'
        || (filter==='cash'   ? m==='amount'
        :  filter==='silent' ? m==='none'
        :  filter==='near'   ? km<=6
        :  filter==='high'   ? (fit==='HIGH'||fit==='MED-HIGH') : true);
      const okTerm = !term || li.dataset.text.includes(term);
      li.hidden = !(ok && okTerm);
      if(!li.hidden) shown++;
    }});
    empty.hidden = shown>0;
  }}
  chips.forEach(c=>c.addEventListener('click',()=>{{
    chips.forEach(o=>o.setAttribute('aria-pressed', String(o===c)));
    filter=c.dataset.filter; apply();
  }}));
  q.addEventListener('input',apply);
  apply();
}})();
</script>
</body>
</html>
"""
(HERE / "index.html").write_text(HTML, encoding="utf-8")
print("wrote index.html", len(HTML), "bytes ·", len(ROWS), "companies")
