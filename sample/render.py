# -*- coding: utf-8 -*-
"""Render one room as a real web page.

`junk=True` wraps the room in the furniture a real site has: nav, cookie
banner, ads, sidebar, footer. The room itself is identical either way, so
the same page can be read two ways - scoped to #game, or naively whole -
and the difference is attributable to extraction, not to the content.
"""
import html, random

NAV = ["Home", "Products", "Pricing", "Solutions", "Enterprise", "Docs", "Blog",
       "Careers", "About us", "Contact", "Support", "Partners", "Press", "Legal", "Status"]
FOOT = ["Terms of Service", "Privacy Policy", "Cookie Policy", "Accessibility",
        "Sitemap", "RSS", "Newsletter", "Investor Relations", "Brand Assets",
        "Security", "Compliance", "Trust Center", "Affiliates", "Resellers",
        "Community", "Events", "Webinars", "Case Studies", "Whitepapers", "API"]
ADS = ["Upgrade to Pro and save 40% this quarter",
       "Join 12,000 teams already shipping faster",
       "Free migration assistance for annual plans",
       "Download the 2026 industry benchmark report"]

CSS = """
*{box-sizing:border-box}body{margin:0;font:15px/1.6 system-ui,'Segoe UI',sans-serif;background:#0f1115;color:#e6e8ec}
nav{background:#171a21;padding:10px 16px;display:flex;flex-wrap:wrap;gap:12px;font-size:13px}
nav a{color:#8b93a7;text-decoration:none}
#game{max-width:720px;margin:32px auto;background:#1b1f28;border:1px solid #2b313d;border-radius:14px;padding:28px}
#goal{font-size:13px;letter-spacing:.08em;text-transform:uppercase;color:#6ee7b7;margin:0 0 6px}
#situation{font-size:20px;line-height:1.5;margin:0 0 24px;color:#f1f3f6}
.opt{display:block;width:100%;text-align:left;margin:10px 0;padding:14px 16px;font:inherit;
     background:#232936;color:#e6e8ec;border:1px solid #333b4a;border-radius:10px;cursor:pointer}
.opt:hover{background:#2c3444;border-color:#4b5563}
#result{margin-top:20px;font-size:17px;font-weight:600;min-height:26px}
aside{max-width:720px;margin:0 auto;color:#5d6478;font-size:13px}
.ad{border:1px dashed #333b4a;border-radius:8px;padding:10px;margin:8px 0}
footer{margin-top:40px;padding:18px 16px;background:#141720;display:flex;flex-wrap:wrap;gap:10px;font-size:12px}
footer a{color:#5d6478;text-decoration:none}
#cookie{position:sticky;top:0;background:#243042;padding:10px 16px;font-size:13px;display:flex;gap:10px;align-items:center}
#cookie button{padding:6px 12px;border-radius:6px;border:1px solid #3a4557;background:#2f3a4d;color:#dfe3ea;cursor:pointer}
"""

JS = """
function pick(el){
  const ok = el.dataset.correct === '1';
  document.getElementById('result').textContent = ok ? 'CORRECT' : 'WRONG';
  document.getElementById('result').style.color = ok ? '#6ee7b7' : '#f87171';
  document.body.dataset.outcome = ok ? 'correct' : 'wrong';
  document.body.dataset.picked = el.textContent.trim();
}
"""


def room_html(goal, situation, correct, distractors, junk=True, seed=0, title="Room"):
    rnd = random.Random(seed)
    options = [(correct, True)] + [(d, False) for d in distractors]
    rnd.shuffle(options)
    buttons = "\n".join(
        f'      <button class="opt" data-correct="{int(ok)}" onclick="pick(this)">{html.escape(t)}</button>'
        for t, ok in options)

    game = f"""    <main id="game">
      <p id="goal">GOAL: {html.escape(goal)}</p>
      <p id="situation">{html.escape(situation)}</p>
{buttons}
      <div id="result"></div>
    </main>"""

    if not junk:
        body = game
    else:
        nav = "".join(f'<a href="#{i}">{html.escape(n)}</a>' for i, n in enumerate(NAV))
        foot = "".join(f'<a href="#f{i}">{html.escape(n)}</a>' for i, n in enumerate(FOOT))
        ads = "".join(f'<div class="ad">{html.escape(a)} <button>Learn more</button></div>' for a in ADS)
        body = f"""    <div id="cookie">We use cookies to improve your experience.
      <button>Accept all</button><button>Reject non-essential</button><button>Manage preferences</button></div>
    <nav>{nav}</nav>
{game}
    <aside>{ads}
      <p>Trusted by teams at Acme, Globex, Initech and 200 other companies. Our platform
         processes over four billion events per day with 99.99% uptime backed by a
         financially guaranteed service level agreement.</p>
      <p>New: the autumn release brings workspace templates, granular role based access
         control, audit log streaming and a redesigned onboarding flow.</p></aside>
    <footer>{foot}</footer>"""

    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<title>{html.escape(title)}</title><style>{CSS}</style><script>{JS}</script></head>
<body>
{body}
</body></html>"""
