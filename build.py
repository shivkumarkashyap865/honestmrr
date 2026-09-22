#!/usr/bin/env python3
"""
HonestMRR static site generator.
Reads data/startups.csv + data/config.json -> writes complete site into site/
No external dependencies. Run: python3 build.py
"""
import csv
import datetime
import re, json, os, html, math
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "site")

# ---------- load ----------
with open(os.path.join(DATA, "config.json"), encoding="utf-8") as f:
    CFG = json.load(f)

# Google-Form / Sheet header aliases -> internal field names
ALIAS = {
    "startup name": "name", "website": "website", "category": "category", "city": "city",
    "one-line description": "description", "monthly revenue (usd)": "mrr_usd",
    "growth % (last 30 days)": "growth_pct", "is your startup for sale?": "for_sale",
    "asking price (usd)": "asking_price_usd", "revenue proof link": "source_url",
    "revenue proof (stripe/razorpay dashboard link)": "source_url",
    "founder email": "founder_email", "x / twitter handle": "x_handle",
    "timestamp": "submitted_ts", "approved": "approved",
}

def _num(v):
    return float(str(v).replace("$", "").replace(",", "").strip() or 0)

rows = []
with open(os.path.join(DATA, "startups.csv"), encoding="utf-8") as f:
    for raw in csv.DictReader(f):
        r = {}
        for k, v in (raw or {}).items():
            if k is None:
                continue
            r[ALIAS.get(k.strip().lower(), k.strip().lower())] = (v or "").strip()
        # approval gate: if sheet has an "approved" column, publish only approved rows
        if "approved" in r and r["approved"].lower() not in ("yes", "y", "true", "1", "approved"):
            continue
        if not r.get("name"):
            continue
        if not r.get("slug"):
            r["slug"] = re.sub(r"[^a-z0-9]+", "-", r["name"].lower()).strip("-")
        if not r.get("submitted_date"):
            r["submitted_date"] = datetime.date.today().isoformat()
        r.setdefault("verification", "")
        try:
            r["mrr_usd"] = _num(r.get("mrr_usd"))
            r["growth_pct"] = _num(r.get("growth_pct"))
            r["asking_price_usd"] = _num(r.get("asking_price_usd"))
        except ValueError:
            continue
        r["for_sale"] = (r.get("for_sale") or "").strip().lower() in ("yes", "true", "1", "y")
        rows.append(r)

rows.sort(key=lambda r: r["mrr_usd"], reverse=True)
for_sale = [r for r in rows if r["for_sale"]]
categories = sorted({r["category"] for r in rows if r.get("category")})

SITE_URL = CFG.get("site_url", "").rstrip("/")
NAME = CFG.get("site_name", "HonestMRR")
ESC = html.escape
LOGO = (NAME[:-3] + "<span>MRR</span>") if NAME.endswith("MRR") else NAME

def fmt_usd(v):
    v = float(v or 0)
    if v <= 0: return "—"
    if v >= 1e9: return f"${v/1e9:.1f}B"
    if v >= 1e6: return f"${v/1e6:.1f}M"
    if v >= 1e3: return f"${v/1e3:.1f}k"
    return f"${v:,.0f}"

def fmt_growth(g):
    g = float(g or 0)
    cls = "up" if g >= 0 else "down"
    sign = "+" if g >= 0 else ""
    return f'<span class="growth {cls}">{sign}{g:.0f}%</span>'

VER_BADGE = {
    "Public Report":  ('<span class="badge b-pub" title="Numbers from public filings / press reports">📰 Public Report</span>'),
    "Founder Verified":('<span class="badge b-ver" title="Founder submitted proof (payment dashboard, screenshots) and we reviewed it">✅ Founder Verified</span>'),
    "Community":      ('<span class="badge b-com" title="Self-reported by the community, not yet verified">👥 Community</span>'),
    "Demo":           ('<span class="badge b-demo">⚠️ DEMO</span>'),
}
def ver_badge(v):
    return VER_BADGE.get((v or "").strip(), f'<span class="badge b-com">{ESC(v or "Unverified")}</span>')

CSS = """
:root{--bg:#0c0906;--text:#f6efe8;--muted:#b9ada1;--stroke:rgba(255,255,255,.13);--glass:rgba(255,255,255,.055);--accent:#ff8a3d;--accent-2:#ff5e1a;--up:#4ade80;--down:#f87171}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;line-height:1.6;min-height:100vh}
body::before{content:"";position:fixed;inset:0;z-index:-1;background:radial-gradient(1100px 620px at 85% -10%,rgba(255,122,47,.20),transparent 60%),radial-gradient(900px 520px at -10% 30%,rgba(255,84,20,.12),transparent 60%),radial-gradient(1000px 700px at 50% 115%,rgba(120,53,15,.25),transparent 65%),#0c0906}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}
.wrap{max-width:1140px;margin:0 auto;padding:0 20px}
header{position:sticky;top:0;z-index:60;background:rgba(12,9,6,.55);backdrop-filter:blur(20px) saturate(140%);-webkit-backdrop-filter:blur(20px) saturate(140%);border-bottom:1px solid var(--stroke)}
.nav{display:flex;align-items:center;gap:22px;padding:14px 0;flex-wrap:wrap}
.logo{font-weight:800;font-size:20px;color:var(--text);letter-spacing:-.5px}
.logo span{color:var(--accent)}
.nav a.nl{color:var(--muted);font-size:14px;font-weight:500}
.nav a.nl:hover{color:var(--text);text-decoration:none}
.nav .spacer{flex:1}
.btn{display:inline-block;padding:10px 18px;border-radius:14px;font-weight:600;font-size:14px;border:1px solid var(--stroke);color:var(--text);background:rgba(255,255,255,.06);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}
.btn:hover{text-decoration:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(255,138,61,.15)}
.btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent-2));color:#210c02;border:none;box-shadow:0 6px 24px rgba(255,110,40,.35)}
.btn-primary:hover{filter:brightness(1.08);box-shadow:0 8px 30px rgba(255,110,40,.45)}
.hero{padding:70px 0 36px;text-align:center}
.hero h1{font-size:42px;line-height:1.12;letter-spacing:-1.2px;margin-bottom:16px}
.hero h1 em{font-style:normal;background:linear-gradient(90deg,var(--accent),#ffc59a);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero p{color:var(--muted);font-size:17px;max-width:660px;margin:0 auto 28px}
.hero .cta{display:flex;gap:12px;justify-content:center;flex-wrap:wrap}
.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:36px 0}
.stat{padding:20px;text-align:center;background:rgba(255,255,255,.055);backdrop-filter:blur(18px) saturate(140%);-webkit-backdrop-filter:blur(18px) saturate(140%);border:1px solid var(--stroke);border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,.30)}
.stat .v{font-size:26px;font-weight:800;color:var(--accent)}
.stat .l{color:var(--muted);font-size:13px}
h2.sec{font-size:24px;margin:46px 0 18px;letter-spacing:-.5px}
table{width:100%;border-collapse:separate;border-spacing:0;background:rgba(255,255,255,.05);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid var(--stroke);border-radius:20px;overflow:hidden}
th{color:var(--muted);font-size:12px;text-transform:uppercase;letter-spacing:.6px;text-align:left;padding:13px 14px;border-bottom:1px solid var(--stroke);background:rgba(255,255,255,.03)}
td{padding:13px 14px;border-bottom:1px solid rgba(255,255,255,.06);font-size:14px;vertical-align:middle}
tr:last-child td{border-bottom:none}
tr:hover td{background:rgba(255,255,255,.04)}
.rev{color:var(--accent);font-weight:700}
.growth.up{color:var(--up);font-weight:600}
.growth.down{color:var(--down);font-weight:600}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:4px 10px;border-radius:99px;border:1px solid var(--stroke);background:rgba(255,255,255,.06);backdrop-filter:blur(8px);white-space:nowrap}
.b-pub{color:#ffd9b8;border-color:rgba(255,138,61,.35)}
.b-ver{color:#a7f3d0;border-color:rgba(74,222,128,.35)}
.b-com{color:#e5ded6}
.b-demo{color:#fca5a5;border-color:rgba(248,113,113,.4)}
.b-sale{color:#fde68a;border-color:rgba(251,191,36,.45);background:rgba(251,191,36,.10)}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:16px}
.card{padding:18px;display:flex;flex-direction:column;gap:10px;background:rgba(255,255,255,.055);backdrop-filter:blur(18px) saturate(140%);-webkit-backdrop-filter:blur(18px) saturate(140%);border:1px solid var(--stroke);border-radius:20px;box-shadow:0 8px 32px rgba(0,0,0,.30);transition:transform .25s,border-color .25s,box-shadow .25s}
.card:hover{transform:translateY(-4px);border-color:rgba(255,138,61,.45);box-shadow:0 12px 40px rgba(0,0,0,.45),0 0 0 1px rgba(255,138,61,.15);text-decoration:none}
.card .top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.card h3{font-size:17px}
.card h3 a{color:var(--text)}
.card .cat{color:var(--muted);font-size:12px}
.card .desc{color:var(--muted);font-size:13px;flex:1;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.card .metrics{display:flex;gap:14px;flex-wrap:wrap;border-top:1px solid rgba(255,255,255,.08);padding-top:12px}
.metric .k{color:var(--muted);font-size:11px;text-transform:uppercase}
.metric .v{font-weight:700;font-size:15px}
.fform{display:flex;flex-direction:column;gap:14px}
.fform label{font-size:13px;color:var(--muted);font-weight:600}
.fform input,.fform select,.fform textarea{width:100%;background:rgba(255,255,255,.06);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--stroke);color:var(--text);padding:11px 13px;border-radius:12px;font-size:14px;font-family:inherit}
.fform textarea{min-height:90px;resize:vertical}
.fform input:focus,.fform select:focus,.fform textarea:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(255,138,61,.15)}
.fform .row2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:640px){.fform .row2{grid-template-columns:1fr}}
.filters{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}
.filters input,.filters select{background:rgba(255,255,255,.06);backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border:1px solid var(--stroke);color:var(--text);padding:10px 12px;border-radius:14px;font-size:14px}
.filters input{flex:1;min-width:200px}
.filters input::placeholder{color:var(--muted)}
.prose{background:rgba(255,255,255,.05);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid var(--stroke);border-radius:22px;padding:28px;margin:24px 0;box-shadow:0 8px 32px rgba(0,0,0,.30)}
.prose h2{font-size:20px;margin:18px 0 8px;color:var(--accent)}
.prose h2:first-child{margin-top:0}
.prose p,.prose li{color:#d8cfc5;font-size:15px}
.prose ul,.prose ol{padding-left:22px;margin:8px 0}
.prose li{margin:4px 0}
footer{border-top:1px solid var(--stroke);margin-top:64px;padding:30px 0;color:var(--muted);font-size:13px;background:rgba(255,255,255,.02)}
footer .wrap{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap}
.crumbs{color:var(--muted);font-size:13px;margin:20px 0}
.detail-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap;margin:24px 0}
.detail-head h1{font-size:32px;letter-spacing:-.5px}
.big-stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:20px 0}
.note{background:rgba(255,138,61,.07);border:1px solid rgba(255,138,61,.30);backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);border-radius:16px;padding:14px 16px;color:var(--muted);font-size:13px;margin:16px 0}
.s3d-wrap{position:relative;height:370px;margin:26px 0 8px;perspective:1500px}
.s3d{position:absolute;inset:0;transform-style:preserve-3d}
.s3card{position:absolute;left:50%;top:8px;width:310px;margin-left:-155px;padding:24px;display:flex;flex-direction:column;gap:8px;background:rgba(255,255,255,.07);backdrop-filter:blur(20px) saturate(150%);-webkit-backdrop-filter:blur(20px) saturate(150%);border:1px solid var(--stroke);border-radius:24px;box-shadow:0 18px 50px rgba(0,0,0,.45);transition:transform .65s cubic-bezier(.22,.75,.2,1),opacity .5s,border-color .3s;will-change:transform}
.s3card:hover{border-color:rgba(255,138,61,.55);text-decoration:none}
.s3rank{font-size:11px;color:var(--muted);letter-spacing:1.5px;text-transform:uppercase}
.s3card h3{font-size:21px;color:var(--text)}
.s3card .cat{color:var(--muted);font-size:12px}
.s3rev{font-size:32px;font-weight:800;color:var(--accent);line-height:1.1;text-shadow:0 0 30px rgba(255,138,61,.35)}
.s3rev small{font-size:13px;color:var(--muted);font-weight:500}
.s3row{display:flex;justify-content:space-between;align-items:center;margin-top:auto;padding-top:10px;border-top:1px solid rgba(255,255,255,.08);font-size:13px}
.s3d-nav{display:flex;gap:10px;justify-content:center;margin:4px 0 10px}
.s3d-nav button{width:46px;height:46px;border-radius:50%;border:1px solid var(--stroke);background:rgba(255,255,255,.07);backdrop-filter:blur(10px);-webkit-backdrop-filter:blur(10px);color:var(--text);font-size:22px;cursor:pointer;transition:border-color .2s,color .2s}
.s3d-nav button:hover{border-color:var(--accent);color:var(--accent)}
@media(max-width:640px){.hero h1{font-size:30px}.table-scroll{overflow-x:auto}.s3d-wrap{height:340px}.s3card{width:255px;margin-left:-127px;padding:18px}.s3rev{font-size:26px}}
"""

gsc_meta = f'<meta name="google-site-verification" content="{CFG["gsc_verification"]}"/>' if CFG.get("gsc_verification") else ""

def page(path, title, desc, body, canonical=None):
    canon = canonical or (SITE_URL + "/" + path if SITE_URL else "")
    canon_tag = f'<link rel="canonical" href="{ESC(canon)}"/>' if canon else ""
    doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{ESC(title)}</title>
<meta name="description" content="{ESC(desc)}"/>
{gsc_meta}
{canon_tag}
<meta property="og:title" content="{ESC(title)}"/>
<meta property="og:description" content="{ESC(desc)}"/>
<meta property="og:type" content="website"/>
{f'<meta property="og:url" content="{ESC(canon)}"/>' if canon else ''}
<link rel="stylesheet" href="{'../' if path.count('/') else ''}assets/style.css"/>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>✅</text></svg>"/>
</head>
<body>
<header><div class="wrap nav">
<a class="logo" href="{'../' if path.count('/') else ''}index.html">📈 {LOGO}</a>
<a class="nl" href="{'../' if path.count('/') else ''}index.html">Leaderboard</a>
<a class="nl" href="{'../' if path.count('/') else ''}browse.html">Buy/Sell</a>
<a class="nl" href="{'../' if path.count('/') else ''}stats.html">Stats</a>
<a class="nl" href="{'../' if path.count('/') else ''}pricing.html">Sponsor</a>
<a class="nl" href="{'../' if path.count('/') else ''}services.html">Services</a>
<a class="nl" href="{'../' if path.count('/') else ''}about.html">About</a>
<div class="spacer"></div>
<a class="btn btn-primary" href="{'../' if path.count('/') else ''}submit.html">+ Add Startup</a>
</div></header>
<main class="wrap">
{body}
</main>
<footer><div class="wrap">
<div>© {date.today().year} {ESC(NAME)} — The database of honest startup revenues.<br/>{ESC(NAME)} is operated by {ESC(CFG.get('owner_name',''))} (sole proprietor), {ESC(CFG.get('owner_location',''))}.{f" Contact: {ESC(CFG['contact_email'])}" if CFG.get('contact_email') else ""}</div>
<div><a href="{'../' if path.count('/') else ''}privacy.html">Privacy Policy</a> · <a href="{'../' if path.count('/') else ''}terms.html">Terms of Service</a></div>
<div>Revenue figures are approximate & from public reports unless marked verified. Not investment advice.</div>
</div></footer>
</body>
</html>"""
    fp = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    with open(fp, "w", encoding="utf-8") as f:
        f.write(doc)

# ---------- index ----------
top = rows[:12]
tr_html = ""
for i, r in enumerate(top, 1):
    tr_html += f"""<tr>
<td>{i}</td>
<td><a href="startup/{ESC(r['slug'])}.html"><strong>{ESC(r['name'])}</strong></a><div class="cat">{ESC(r.get('city',''))}</div></td>
<td>{ESC(r.get('category',''))}</td>
<td class="rev">{fmt_usd(r['mrr_usd'])}<div class="cat">/month</div></td>
<td>{fmt_growth(r['growth_pct'])}</td>
<td>{ver_badge(r.get('verification'))}</td>
</tr>"""

sale_cards = ""
for r in for_sale[:6]:
    mult = (r["asking_price_usd"] / (r["mrr_usd"] * 12)) if r["mrr_usd"] > 0 else 0
    sale_cards += f"""<div class="card">
<div class="top"><div><h3><a href="startup/{ESC(r['slug'])}.html">{ESC(r['name'])}</a></h3>
<div class="cat">{ESC(r.get('category',''))} · {ESC(r.get('city',''))}</div></div>
<span class="badge b-sale">FOR SALE</span></div>
<div class="desc">{ESC(r.get('description',''))}</div>
<div class="metrics">
<div class="metric"><div class="k">Revenue/mo</div><div class="v rev">{fmt_usd(r['mrr_usd'])}</div></div>
<div class="metric"><div class="k">Asking</div><div class="v">{fmt_usd(r['asking_price_usd'])}</div></div>
<div class="metric"><div class="k">Multiple</div><div class="v">{mult:.1f}x</div></div>
</div></div>"""

total_mrr = sum(r["mrr_usd"] for r in rows)
slider_cards = ""
for i2, r2 in enumerate(rows[:8]):
    slider_cards += f"""<a class="s3card" href="startup/{ESC(r2['slug'])}.html">
<div class="s3rank">#{i2+1} on the leaderboard</div>
<h3>{ESC(r2['name'])}</h3>
<div class="cat">{ESC(r2.get('category',''))} · {ESC(r2.get('city',''))}</div>
<div class="s3rev">{fmt_usd(r2['mrr_usd'])}<small> /month</small></div>
<div class="s3row"><span>Growth {fmt_growth(r2['growth_pct'])}</span>{ver_badge(r2.get('verification'))}</div>
</a>"""

home = f"""
<div class="hero">
<h1>The database of <em>honest startup revenues</em></h1>
<p>Revenue, MRR and growth of SaaS, apps and digital businesses worldwide — no fake screenshots, only honest numbers from public filings and founder-verified submissions.</p>
<div class="cta">
<a class="btn btn-primary" href="browse.html">Explore the marketplace</a>
<a class="btn" href="submit.html">Add your startup</a>
</div>
</div>
<div class="stats-row">
<div class="stat"><div class="v">{len(rows)}</div><div class="l">Startups tracked</div></div>
<div class="stat"><div class="v">{fmt_usd(total_mrr)}</div><div class="l">Combined monthly revenue</div></div>
<div class="stat"><div class="v">{len(for_sale)}</div><div class="l">Listed for sale</div></div>
<div class="stat"><div class="v">{len(categories)}</div><div class="l">Categories</div></div>
</div>
<h2 class="sec">✨ Featured startups</h2>
<div class="s3d-wrap"><div class="s3d" id="s3d">{slider_cards}</div></div>
<div class="s3d-nav"><button id="s3prev" aria-label="Previous">‹</button><button id="s3next" aria-label="Next">›</button></div>
<script src="assets/slider.js"></script>
<h2 class="sec">🏆 Revenue Leaderboard</h2>
<div class="table-scroll"><table>
<thead><tr><th>#</th><th>Startup</th><th>Category</th><th>Revenue</th><th>Growth</th><th>Verification</th></tr></thead>
<tbody>{tr_html}</tbody>
</table></div>
<p style="margin-top:12px"><a href="stats.html">See full stats →</a></p>
<h2 class="sec">💰 Startups for sale</h2>
<div class="cards">{sale_cards if sale_cards else '<div class="note">No startups listed for sale yet. <a href="submit.html">Be the first to list →</a></div>'}</div>
<p style="margin-top:12px"><a href="browse.html">Browse all listings →</a></p>
<h2 class="sec">Categories</h2>
<div class="cards" style="grid-template-columns:repeat(auto-fill,minmax(180px,1fr))">
{''.join(f'<a class="card" style="text-align:center" href="browse.html#{ESC(c.lower().replace(" ","-"))}">{ESC(c)} <span class="cat">({sum(1 for r in rows if r["category"]==c)})</span></a>' for c in categories)}
</div>
"""
page("index.html", f"{NAME} — {CFG['tagline']}", CFG["description"], home)

# ---------- browse ----------
all_cards = ""
for r in rows:
    mult = (r["asking_price_usd"] / (r["mrr_usd"] * 12)) if (r["mrr_usd"] > 0 and r["asking_price_usd"] > 0) else 0
    sale_badge = '<span class="badge b-sale">FOR SALE</span>' if r["for_sale"] else ""
    mult_html = f'<div class="metric"><div class="k">Asking</div><div class="v">{fmt_usd(r["asking_price_usd"])}</div></div><div class="metric"><div class="k">Multiple</div><div class="v">{mult:.1f}x</div></div>' if r["for_sale"] else ""
    all_cards += f"""<div class="card item" data-name="{ESC(r['name'].lower())}" data-cat="{ESC(r.get('category','').lower())}" data-sale="{'1' if r['for_sale'] else '0'}" data-mrr="{r['mrr_usd']}" data-growth="{r['growth_pct']}" id="{ESC(r.get('category','').lower().replace(' ','-'))}">
<div class="top"><div><h3><a href="startup/{ESC(r['slug'])}.html">{ESC(r['name'])}</a></h3>
<div class="cat">{ESC(r.get('category',''))} · {ESC(r.get('city',''))}</div></div>{sale_badge}</div>
<div class="desc">{ESC(r.get('description',''))}</div>
<div class="metrics">
<div class="metric"><div class="k">Revenue/mo</div><div class="v rev">{fmt_usd(r['mrr_usd'])}</div></div>
<div class="metric"><div class="k">Growth</div><div class="v">{fmt_growth(r['growth_pct'])}</div></div>
{mult_html}
</div>
<div>{ver_badge(r.get('verification'))}</div>
</div>"""

cat_opts = "".join(f'<option value="{ESC(c.lower())}">{ESC(c)}</option>' for c in categories)
browse = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">Buy & sell profitable startups</h1>
<p>{len(rows)} startups · {len(for_sale)} for sale · revenue data from public filings and founder-verified submissions</p>
</div>
<div class="filters">
<input id="q" type="search" placeholder="Search startups..."/>
<select id="cat"><option value="">All categories</option>{cat_opts}</select>
<select id="sale"><option value="">All listings</option><option value="1">For sale only</option></select>
<select id="sort"><option value="mrr">Sort: Revenue</option><option value="growth">Sort: Growth</option></select>
</div>
<div class="cards" id="grid">{all_cards}</div>
<script src="assets/browse.js"></script>
"""
page("browse.html", f"Buy and Sell SaaS Startups — {NAME}", "Browse verified startups for acquisition. Filter by category, revenue, growth and asking price.", browse)

# ---------- stats ----------
cat_stats = {}
for r in rows:
    c = r.get("category") or "Other"
    cat_stats.setdefault(c, {"n": 0, "mrr": 0.0})
    cat_stats[c]["n"] += 1
    cat_stats[c]["mrr"] += r["mrr_usd"]
cat_rows = "".join(
    f'<tr><td>{ESC(c)}</td><td>{d["n"]}</td><td class="rev">{fmt_usd(d["mrr"])}</td><td class="rev">{fmt_usd(d["mrr"]/d["n"] if d["n"] else 0)}</td></tr>'
    for c, d in sorted(cat_stats.items(), key=lambda kv: kv[1]["mrr"], reverse=True))
top10 = "".join(
    f'<tr><td>{i}</td><td><a href="startup/{ESC(r["slug"])}.html">{ESC(r["name"])}</a></td><td>{ESC(r.get("category",""))}</td><td class="rev">{fmt_usd(r["mrr_usd"])}</td><td>{fmt_growth(r["growth_pct"])}</td></tr>'
    for i, r in enumerate(rows[:10], 1))
avg_mrr = total_mrr / len(rows) if rows else 0
growth_vals = [r["growth_pct"] for r in rows]
avg_g = sum(growth_vals) / len(growth_vals) if growth_vals else 0
stats_body = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">Startup Revenue Stats</h1>
<p>Aggregated from {len(rows)} tracked startups. Updated regularly.</p>
</div>
<div class="stats-row">
<div class="stat"><div class="v">{fmt_usd(total_mrr)}</div><div class="l">Total monthly revenue</div></div>
<div class="stat"><div class="v">{fmt_usd(avg_mrr)}</div><div class="l">Avg monthly revenue</div></div>
<div class="stat"><div class="v">{avg_g:+.0f}%</div><div class="l">Avg growth (MoM)</div></div>
<div class="stat"><div class="v">{fmt_usd(sum(r['asking_price_usd'] for r in for_sale))}</div><div class="l">Total asking (for sale)</div></div>
</div>
<h2 class="sec">Top 10 by revenue</h2>
<div class="table-scroll"><table><thead><tr><th>#</th><th>Startup</th><th>Category</th><th>Revenue/mo</th><th>Growth</th></tr></thead><tbody>{top10}</tbody></table></div>
<h2 class="sec">By category</h2>
<div class="table-scroll"><table><thead><tr><th>Category</th><th>Startups</th><th>Total revenue/mo</th><th>Avg revenue/mo</th></tr></thead><tbody>{cat_rows}</tbody></table></div>
<div class="note">Figures are approximate. Public-company numbers come from filings/press; startup submissions carry a verification badge. Data refreshes daily.</div>
"""
page("stats.html", f"Stats — SaaS Revenue Benchmarks — {NAME}", "Revenue benchmarks for SaaS startups: totals, averages, growth and category breakdowns.", stats_body)

# ---------- submit ----------
form_url = CFG.get("submit_form_url") or "#"
submit = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">Add your startup</h1>
<p>Get listed free. Verified startups get a badge, more traffic, and priority placement in the buy/sell marketplace.</p>
<form class="fform prose" style="margin-top:20px" action="https://formsubmit.co/{ESC(CFG.get('contact_email',''))}" method="POST">
<input type="hidden" name="_subject" value="New startup submission — HonestMRR"/>
<input type="hidden" name="_captcha" value="false"/>
<input type="hidden" name="_template" value="table"/>
<input type="hidden" name="_next" value="{SITE_URL}/thanks.html"/>
<label>Startup name *</label><input name="Startup name" required placeholder="Example: DemoApp"/>
<div class="row2">
<div><label>Website *</label><input name="Website" required placeholder="https://..."/></div>
<div><label>City</label><input name="City" placeholder="Indore"/></div>
</div>
<label>Category *</label><select name="Category" required><option value="">Choose...</option><option>SaaS</option><option>Fintech</option><option>Marketing</option><option>Developer Tools</option><option>Artificial Intelligence</option><option>E-commerce</option><option>Health & Fitness</option><option>Social Media</option><option>Productivity</option><option>Customer Support</option><option>Other</option></select>
<label>One-line description *</label><textarea name="Description" required placeholder="What does your startup do?"></textarea>
<div class="row2">
<div><label>Monthly revenue (USD) *</label><input name="Monthly revenue USD" type="number" required placeholder="2500"/></div>
<div><label>Growth % (30 days)</label><input name="Growth pct" type="number" placeholder="12"/></div>
</div>
<div class="row2">
<div><label>For sale?</label><select name="For sale"><option>No</option><option>Yes</option></select></div>
<div><label>Asking price (USD)</label><input name="Asking price USD" type="number" placeholder="30000"/></div>
</div>
<label>Revenue proof link * (Google Drive/Dropbox screenshot link)</label><input name="Revenue proof link" required placeholder="https://drive.google.com/..."/>
<div class="row2">
<div><label>Founder email *</label><input name="Founder email" type="email" required placeholder="you@email.com"/></div>
<div><label>X / Twitter handle</label><input name="X handle" placeholder="@..."/></div>
</div>
<button class="btn btn-primary" type="submit" style="margin-top:6px">Submit for review →</button>
<p style="color:var(--muted);font-size:12px;margin-top:10px">Review within 7 days. Proof bhejne walon ko ✅ Founder Verified badge milta hai. <a href="pricing.html">⭐ Get featured</a></p>
</form>
</div>
<div class="prose">
<h2>How verification works</h2>
<ul>
<li><strong>📰 Public Report</strong> — numbers from stock filings, ROC filings or credible press. We add these ourselves with a source link.</li>
<li><strong>✅ Founder Verified</strong> — you submit proof: Razorpay/Stripe/Lemon Squeezy dashboard export, payment gateway screenshots, or a read-only revenue link. We review manually within 7 days.</li>
<li><strong>👥 Community</strong> — self-reported, shown with an unverified badge until proof is submitted.</li>
</ul>
<h2>What you get</h2>
<ul>
<li>A public profile page (great for your own SEO + investor credibility)</li>
<li>Position on the revenue leaderboard</li>
<li>Access to buyers browsing the marketplace if you ever want to sell</li>
</ul>
<h2>Why list?</h2>
<p>Founders post revenue screenshots on X every day — but screenshots can be faked. A verified listing here is proof-of-work that buyers, investors and customers can trust.</p>
</div>
"""
page("submit.html", f"Add your startup — {NAME}", "Submit your Indian startup's revenue for verification and get listed on the leaderboard free.", submit)

# ---------- about ----------
about = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">About {NAME}</h1>
<p>No fake screenshots. Only honest numbers.</p>
</div>
<div class="prose">
<h2>Mission</h2>
<p>Thousands of founders post revenue screenshots every day — and most can be faked. {NAME} is building the public ledger of what startups actually earn: verified wherever possible, sourced from public filings otherwise. We started with India-origin SaaS (Zoho, Freshworks, Postman, Razorpay...) and are expanding worldwide.</p>
<h2>Three trust tiers</h2>
<ol>
<li><strong>📰 Public Report</strong> — filings & press, with source link.</li>
<li><strong>✅ Founder Verified</strong> — payment-provider proof reviewed by us.</li>
<li><strong>👥 Community</strong> — self-reported, clearly marked.</li>
</ol>
<h2>For buyers & sellers</h2>
<p>The Buy/Sell section lists profitable startups for acquisition. Sellers get exposure to thousands of visitors; buyers get numbers they can trust. {len(for_sale)} startups currently listed.</p>
<h2>Operator</h2>
<p>{ESC(NAME)} is operated by {ESC(CFG.get('owner_name',''))}, a sole proprietor based in {ESC(CFG.get('owner_location',''))}. The business sells advertising and sponsorship placements on this website along with featured-listing services.</p>
<h2>Contact</h2>
<p>{('Email: ' + ESC(CFG['contact_email'])) if CFG.get('contact_email') else 'Contact details coming soon. Follow us on X.'}</p>
</div>
"""
page("about.html", f"About — {NAME}", "Why HonestMRR exists: transparent, verified revenue data for startups worldwide. No fake screenshots — only honest numbers.", about)

# ---------- detail pages ----------
for r in rows:
    slug = r["slug"]
    mult = (r["asking_price_usd"] / (r["mrr_usd"] * 12)) if (r["mrr_usd"] > 0 and r["asking_price_usd"] > 0) else 0
    src = f'<p style="margin-top:8px"><a href="{ESC(r["source_url"])}" target="_blank" rel="noopener nofollow">View source →</a></p>' if r.get("source_url") else ""
    city_part = (" (" + r["city"] + ")") if r.get("city") else ""
    sale_block = f"""
    <div class="note" style="border-color:#78350f;background:#2b1d0533">
      <strong style="color:var(--sale)">💰 This startup is for sale</strong><br/>
      Asking price: <strong>{fmt_usd(r['asking_price_usd'])}</strong> · Multiple: <strong>{mult:.1f}x</strong> annual revenue<br/>
      Interested? <a href="../submit.html">Contact via {NAME}</a>.
    </div>""" if r["for_sale"] else ""
    similar = [x for x in rows if x["category"] == r.get("category") and x["slug"] != slug][:3]
    sim_html = "".join(f'<li><a href="{ESC(x["slug"])}.html">{ESC(x["name"])}</a> — {fmt_usd(x["mrr_usd"])}/mo</li>' for x in similar)
    ld = {
        "@context": "https://schema.org", "@type": "Organization",
        "name": r["name"], "url": r.get("website", ""),
        "description": r.get("description", ""),
        "address": {"@type": "PostalAddress", "addressLocality": r.get("city", "")},
    }
    body = f"""
<div class="crumbs"><a href="../index.html">Home</a> / <a href="../browse.html">Startups</a> / {ESC(r['name'])}</div>
<div class="detail-head">
<div><h1>{ESC(r['name'])}</h1>
<div class="cat">{ESC(r.get('category',''))} · {ESC(r.get('city',''))} {('· <a href="'+ESC(r.get('website',''))+'" rel="nofollow noopener" target="_blank">website ↗</a>') if r.get('website') else ''}</div>
<div style="margin-top:8px">{ver_badge(r.get('verification'))}</div></div>
<a class="btn btn-primary" href="../submit.html">Claim / Update this listing</a>
</div>
<div class="big-stats">
<div class="stat"><div class="v">{fmt_usd(r['mrr_usd'])}</div><div class="l">Revenue / month (approx)</div></div>
<div class="stat"><div class="v">{fmt_usd(r['mrr_usd']*12)}</div><div class="l">Annualized revenue</div></div>
<div class="stat"><div class="v">{('+' if r['growth_pct']>=0 else '')}{r['growth_pct']:.0f}%</div><div class="l">Growth (MoM)</div></div>
{'<div class="stat"><div class="v">'+fmt_usd(r['asking_price_usd'])+'</div><div class="l">Asking price</div></div>' if r['for_sale'] else ''}
</div>
{sale_block}
<div class="prose">
<h2>About {ESC(r['name'])}</h2>
<p>{ESC(r.get('description',''))}</p>
{src}
</div>
{'<h2 class="sec">Similar startups in '+ESC(r.get("category",""))+'</h2><div class="prose"><ul>'+sim_html+'</ul></div>' if sim_html else ''}
<script type="application/ld+json">{json.dumps(ld)}</script>
"""
    page(f"startup/{slug}.html", f"{r['name']} Revenue & MRR — {NAME}", f"{r['name']}{city_part} makes approximately {fmt_usd(r['mrr_usd'])}/month. See verified revenue, growth and details on {NAME}.", body)


# ---------- pricing / payments ----------
upi = (CFG.get("upi_id") or "").strip()
rzp = (CFG.get("razorpay_link") or "").strip()
ppm = (CFG.get("paypal_link") or "").strip()
wise = (CFG.get("wise_link") or "").strip()
pay_btns = []
if upi:
    pay_btns.append(f'<a class="btn btn-primary" href="upi://pay?pa={ESC(upi)}&pn={ESC(NAME)}&cu=INR">📱 Pay via UPI (India)</a>')
if rzp:
    pay_btns.append(f'<a class="btn" href="{ESC(rzp)}" target="_blank" rel="noopener">💳 Card / NetBanking / Intl (Razorpay)</a>')
if ppm:
    pay_btns.append(f'<a class="btn" href="{ESC(ppm)}" target="_blank" rel="noopener">🌍 PayPal (International)</a>')
if wise:
    pay_btns.append(f'<a class="btn" href="{ESC(wise)}" target="_blank" rel="noopener">🏦 Wise bank transfer (International)</a>')
pay_html = " ".join(pay_btns) if pay_btns else '<div class="note">Payment links setup me hai. Tab tak <a href="submit.html">submit page</a> se contact karein.</div>'
qr_html = ""
if upi:
    qr_html = f"""<div style="text-align:center;margin:18px 0">
<canvas id="upiqr" style="border-radius:16px;background:#fff;padding:12px"></canvas>
<div class="cat" style="margin-top:8px">UPI ID: <strong>{ESC(upi)}</strong> (scan karein ya copy karein)</div>
<script src="https://cdn.jsdelivr.net/npm/qrious@4.0.2/dist/qrious.min.js"></script>
<script>if(window.QRious){{new QRious({{element:document.getElementById('upiqr'),value:'upi://pay?pa={ESC(upi)}&pn={ESC(NAME)}&cu=INR',size:190,background:'#ffffff',foreground:'#1a120b'}});}}</script>
</div>"""

pricing = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">Sponsor & get featured</h1>
<p>Support the open startup database — aur hazards of verified-revenue visitors ke saamne apna product ya startup rakho.</p>
</div>
<div class="cards">
<div class="card"><div class="top"><h3>🏠 Homepage sponsor slot</h3><span class="badge b-sale">BEST VALUE</span></div>
<div class="desc">Logo + link har page par (header sponsor strip). Dev-tools, hosting, payment, CA services — perfect audience of founders.</div>
<div class="metrics"><div class="metric"><div class="k">Price</div><div class="v rev">₹15,000/mo</div></div><div class="metric"><div class="k">or</div><div class="v">$200/mo</div></div></div></div>
<div class="card"><div class="top"><h3>⭐ Featured listing</h3></div>
<div class="desc">Aapka startup 3D slider + homepage par 30 din tak featured, "Featured" badge ke saath.</div>
<div class="metrics"><div class="metric"><div class="k">One-time</div><div class="v rev">₹3,000</div></div><div class="metric"><div class="k">or</div><div class="v">$40</div></div></div></div>
<div class="card"><div class="top"><h3>✅ Verified badge fast-track</h3></div>
<div class="desc">Revenue proof review 48 ghante me priority ke saath — badge + profile page turant.</div>
<div class="metrics"><div class="metric"><div class="k">One-time</div><div class="v rev">₹1,500</div></div><div class="metric"><div class="k">or</div><div class="v">$20</div></div></div></div>
<div class="card"><div class="top"><h3>💰 Startup becho</h3><span class="badge b-ver">FREE LISTING</span></div>
<div class="desc">Listing bilkul free. Deal close hone par sirf 3% success fee — koi upfront cost nahi.</div>
<div class="metrics"><div class="metric"><div class="k">Upfront</div><div class="v rev">₹0</div></div><div class="metric"><div class="k">On sale</div><div class="v">3%</div></div></div></div>
</div>
<h2 class="sec">💳 Payment methods</h2>
<div class="prose">
<p>{pay_html}</p>
{qr_html}
<p style="color:var(--muted);font-size:13px">Payment ke baad apni receipt + listing details submit form se bhejein — 24 ghante me live. International invoices (USD, wire/PayPal) available on request.</p>
</div>
"""
page("pricing.html", f"Sponsor & Featured Pricing — {NAME}", "Sponsor HonestMRR: homepage sponsor slots, featured listings and verified badge fast-track. Pay via UPI, Razorpay, PayPal or Wise.", pricing)


# ---------- legal pages ----------
privacy = f"""
<div class="hero" style="padding:40px 0 10px"><h1 style="font-size:32px">Privacy Policy</h1>
<p>Last updated: {date.today().strftime('%d %B %Y')}</p></div>
<div class="prose">
<h2>What we collect</h2>
<p>{ESC(NAME)} is a static informational website. We do not use tracking cookies and do not require accounts. If you submit your startup for listing (via our submission form), we collect only the details you provide: startup name, website, category, description, revenue figures and your contact handle, solely for the purpose of publishing and verifying your listing.</p>
<h2>Payments</h2>
<p>All payments (UPI, card, PayPal, Wise) are processed by regulated third-party payment providers. {ESC(NAME)} never sees or stores card numbers, bank credentials or UPI PINs.</p>
<h2>Data published</h2>
<p>Revenue figures are published only from public filings/press reports or with the founder's explicit submission. Founders may request correction or removal of their listing at any time by contacting the operator.</p>
<h2>Operator</h2>
<p>{ESC(NAME)} is operated by {ESC(CFG.get('owner_name',''))} (sole proprietor), {ESC(CFG.get('owner_location',''))}.{f" Email: {ESC(CFG['contact_email'])}" if CFG.get('contact_email') else ""}</p>
</div>
"""
page("privacy.html", f"Privacy Policy — {NAME}", f"How {NAME} handles data: no tracking cookies, founder-submitted listings, third-party payment processing.", privacy)

terms = f"""
<div class="hero" style="padding:40px 0 10px"><h1 style="font-size:32px">Terms of Service</h1>
<p>Last updated: {date.today().strftime('%d %B %Y')}</p></div>
<div class="prose">
<h2>1. About the service</h2>
<p>{ESC(NAME)} publishes approximate revenue data for startups from public sources and founder submissions, and provides a platform where startups may be listed for acquisition. Data is provided for informational purposes only and is not investment, legal or tax advice.</p>
<h2>2. Listings</h2>
<p>Founders submitting listings warrant that the information provided is accurate and that they have the right to share it. We may verify, edit, badge or remove any listing at our discretion. Paid featured placements are clearly marked and do not alter verified revenue figures.</p>
<h2>3. Advertising & sponsorship</h2>
<p>Sponsor slots are sold on a monthly basis. Sponsored content is labelled. Sponsors are responsible for the legality of their own products and claims.</p>
<h2>4. Marketplace</h2>
<p>Acquisition transactions are concluded directly between buyer and seller. {ESC(NAME)} acts only as a listing platform and charges a success fee where stated. We are not a party to any acquisition agreement.</p>
<h2>5. Liability</h2>
<p>Figures are approximate and sourced in good faith; we accept no liability for decisions taken on the basis of published data. Operated by {ESC(CFG.get('owner_name',''))} (sole proprietor), {ESC(CFG.get('owner_location',''))}, governed by the laws of India.</p>
</div>
"""
page("terms.html", f"Terms of Service — {NAME}", f"Terms of use for {NAME}: listings, sponsorship, marketplace and liability.", terms)


# ---------- services page ----------
services = f"""
<div class="hero" style="padding:40px 0 10px">
<h1 style="font-size:32px">Hire the founder: AI agents, websites & chatbots</h1>
<p>This entire site — glassmorphism UI, 3D slider, auto-updating data pipeline, SEO — was built solo by Shivkumar Mallah. <strong>HonestMRR is itself the portfolio.</strong> Same quality, for your business.</p>
</div>
<div class="cards">
<div class="card"><div class="top"><h3>🤖 AI Chatbot</h3><span class="badge b-ver">7-DAY DELIVERY</span></div>
<div class="desc">WhatsApp + website chatbot jo aapke customers ke sawaalon ke jawab khud deta hai — lead capture, booking, support. Trained on your business data.</div>
<div class="metrics"><div class="metric"><div class="k">Starts at</div><div class="v rev">₹15,000</div></div></div></div>
<div class="card"><div class="top"><h3>🌐 Business Website</h3><span class="badge b-ver">7-DAY DELIVERY</span></div>
<div class="desc">Modern, fast, mobile-first website (isi site jaisi glassmorphism design). SEO-ready, payment buttons ke saath. Hosting setup included.</div>
<div class="metrics"><div class="metric"><div class="k">Starts at</div><div class="v rev">₹20,000</div></div></div></div>
<div class="card"><div class="top"><h3>🧠 AI Agents & Automation</h3></div>
<div class="desc">Custom AI agents: lead generation, email automation, data extraction, internal ops. Jo ghanton ka kaam hai wo minutes me.</div>
<div class="metrics"><div class="metric"><div class="k">Starts at</div><div class="v rev">₹35,000</div></div></div></div>
<div class="card"><div class="top"><h3>🔧 Maintenance + SEO</h3></div>
<div class="desc">Monthly care: updates, backups, speed, search-console monitoring, content tweaks. Aapki site hamesha zinda aur rank karti rahe.</div>
<div class="metrics"><div class="metric"><div class="k">Monthly</div><div class="v rev">₹5,000</div></div></div></div>
</div>
<h2 class="sec">Kaise kaam hota hai</h2>
<div class="prose">
<ol>
<li><strong>DM / email</strong> karo: {f'{ESC(CFG["contact_email"])}' if CFG.get('contact_email') else 'site ke About page se contact karo'} — requirement batao (10 min call)</li>
<li><strong>Fixed quote</strong> milta hai 24 ghante me — koi hidden charge nahi</li>
<li><strong>50% advance</strong> (UPI: {ESC(CFG.get('upi_id','')) or 'on request'}) → kaam shuru</li>
<li><strong>Delivery + 50%</strong> — 7-14 din me live. 15 din ka free support saath me.</li>
</ol>
<p style="color:var(--muted);font-size:13px">International clients: USD invoices via Wise/PayPal, purpose code P1007. Portfolio = yahi website + HonestMRR data pipeline.</p>
</div>
"""
page("services.html", f"AI Agents, Websites & Chatbots by Shivkumar — {NAME}", "Hire the founder of HonestMRR: AI chatbots, modern business websites, AI agents and automation. 7-day delivery, fixed pricing, UPI or Wise.", services)


# ---------- thanks page ----------
thanks = f"""
<div class="hero" style="padding:60px 0 30px">
<h1 style="font-size:32px">🎉 Submission received!</h1>
<p>Shukriya! Aapki listing review queue me hai — <strong>7 din ke andar</strong> email par jawab aayega. Revenue proof valid hua to ✅ Founder Verified badge ke saath live ho jayegi.</p>
<div class="cta" style="margin-top:20px"><a class="btn btn-primary" href="index.html">Leaderboard dekhein</a><a class="btn" href="browse.html">Marketplace browse karein</a></div>
</div>
"""
page("thanks.html", f"Submission received — {NAME}", "Thank you for submitting your startup to HonestMRR. Review within 7 days.", thanks)

# ---------- smart 404: auto-redirect to home ----------
notfound = """
<div class="container" style="text-align:center;padding:80px 20px;">
<meta http-equiv="refresh" content="3;url=/honestmrr/">
<h1 style="font-size:34px;">Page moved 🔄</h1>
<p style="color:var(--muted);margin:14px 0 26px;">Taking you to the HonestMRR home in 3 seconds…</p>
<a class="btn btn-primary" href="/honestmrr/">Go to home now →</a>
</div>
<script>setTimeout(function(){location.replace("/honestmrr/");},3000);</script>
"""
page("404.html", f"Page not found — {NAME}", "Redirecting you to HonestMRR home.", notfound)

# ---------- sitemap / robots ----------
urls = ["index.html", "browse.html", "stats.html", "submit.html", "about.html", "pricing.html", "thanks.html", "privacy.html", "terms.html", "services.html"] + [f"startup/{r['slug']}.html" for r in rows]
if SITE_URL:
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{SITE_URL}/{u}</loc></url>\n" for u in urls)
    sm += "</urlset>"
    with open(os.path.join(OUT, "sitemap.xml"), "w") as f:
        f.write(sm)
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")

# ---------- assets ----------
os.makedirs(os.path.join(OUT, "assets"), exist_ok=True)
with open(os.path.join(OUT, "assets", "style.css"), "w") as f:
    f.write(CSS)
with open(os.path.join(OUT, "assets", "browse.js"), "w") as f:
    f.write("""
(function(){
  var q=document.getElementById('q'),cat=document.getElementById('cat'),sale=document.getElementById('sale'),sort=document.getElementById('sort'),grid=document.getElementById('grid');
  function apply(){
    var items=Array.prototype.slice.call(grid.children);
    var qs=(q.value||'').toLowerCase(),cs=cat.value||'',ss=sale.value||'';
    items.forEach(function(el){
      var ok=(!qs||el.dataset.name.indexOf(qs)>-1)&&(!cs||el.dataset.cat===cs)&&(!ss||el.dataset.sale===ss);
      el.style.display=ok?'':'none';
    });
    var key=sort.value;
    items.sort(function(a,b){return parseFloat(b.dataset[key])-parseFloat(a.dataset[key]);});
    items.forEach(function(el){grid.appendChild(el);});
  }
  [q,cat,sale,sort].forEach(function(el){el.addEventListener('input',apply);el.addEventListener('change',apply);});
})();
""")


with open(os.path.join(OUT, "assets", "slider.js"), "w") as f:
    f.write("""
(function(){
  var stage=document.getElementById('s3d');
  if(!stage) return;
  var cards=Array.prototype.slice.call(stage.children);
  var n=cards.length, active=0, timer=null;
  function layout(){
    cards.forEach(function(el,i){
      var off=i-active;
      if(off>n/2) off-=n;
      if(off<-n/2) off+=n;
      var a=Math.abs(off);
      el.style.transform='translateX('+(off*58)+'%) translateZ('+(-a*175)+'px) rotateY('+(-off*34)+'deg)';
      el.style.opacity=a>2?0:1-a*0.22;
      el.style.zIndex=String(100-a);
      el.style.pointerEvents=a>2?'none':'auto';
    });
  }
  function go(d){active=(active+d+n)%n;layout();}
  function restart(){if(timer)clearInterval(timer);timer=setInterval(function(){go(1);},3800);}
  document.getElementById('s3prev').addEventListener('click',function(){go(-1);restart();});
  document.getElementById('s3next').addEventListener('click',function(){go(1);restart();});
  var sx=null;
  stage.addEventListener('touchstart',function(e){sx=e.touches[0].clientX;},{passive:true});
  stage.addEventListener('touchend',function(e){
    if(sx===null)return;
    var dx=e.changedTouches[0].clientX-sx;
    if(Math.abs(dx)>40) go(dx<0?1:-1);
    sx=null;restart();
  },{passive:true});
  stage.addEventListener('mouseenter',function(){if(timer)clearInterval(timer);});
  stage.addEventListener('mouseleave',restart);
  layout();restart();
})();
""")

# Google Search Console verification files (data/google*.html) site root par copy karo
import shutil as _sh
for _f in os.listdir(DATA):
    if _f.startswith("google") and _f.endswith(".html"):
        _sh.copy(os.path.join(DATA, _f), os.path.join(OUT, _f))

print(f"Built {len(urls)} pages into {OUT}")
