"""Build The Flint Focus from content/*.json.  Run: python3 build.py"""
import json, glob, os, html

ROOT = os.path.dirname(os.path.abspath(__file__))
site = json.load(open(os.path.join(ROOT, "content", "site.json")))
weeks = [json.load(open(f)) for f in glob.glob(os.path.join(ROOT, "content", "weeks", "*.json"))]
weeks.sort(key=lambda w: w["date"], reverse=True)
GATE_WEEK = weeks[0]["date"] if weeks else ""
e = html.escape


def page(title, body, prefix="", current="", script=False):
    def nav(href, label, key):
        cur = ' aria-current="page"' if key == current else ""
        return f'<a href="{prefix}{href}"{cur}>{label}</a>'
    js = f'<script src="{prefix}assets/app.js" defer></script>' if script else ""
    return f"""<!doctype html>
<html lang="en" class="locked">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)} | {e(site['name'])}</title>
<link rel="icon" href="{prefix}assets/lens.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@75..100,500..800&family=Figtree:wght@400;500;600&display=swap">
<link rel="stylesheet" href="{prefix}assets/style.css">
<script>window.FOCUS_WEEK="{GATE_WEEK}";</script>
<script src="{prefix}assets/gate.js"></script>
<noscript><style>html.locked .shell{{visibility:visible}}#gate{{display:none}}</style></noscript>
{js}
</head>
<body>
<div id="gate" role="dialog" aria-modal="true" aria-labelledby="gate-h">
  <form class="gate-card" novalidate>
    <svg class="gate-lens" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M15 15l5.5 5.5" stroke="currentColor" stroke-width="2.6" stroke-linecap="round"/></svg>
    <h1 id="gate-h">{e(site['name'])}</h1>
    <p>Enter this week’s PIN.</p>
    <label for="gate-in" class="sr">PIN</label>
    <input id="gate-in" inputmode="numeric" autocomplete="off" placeholder="PIN">
    <button type="submit">Open</button>
    <p class="gate-msg" aria-live="polite"></p>
  </form>
</div>
<div class="shell">
<a class="skip" href="#main">Skip to content</a>
<header class="top">
  <div class="wrap top-inner">
    <a class="brand" href="{prefix}index.html"><svg class="mark" viewBox="0 0 24 24" aria-hidden="true"><circle cx="10" cy="10" r="6.5" fill="none" stroke="currentColor" stroke-width="2.6"/><path d="M15 15l5.5 5.5" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>{e(site['name'])}<span class="team">{e(site['team'])}</span></a>
    <nav aria-label="Main">{nav('index.html', 'This Week', 'this')}{nav('archive.html', 'Past Weeks', 'archive')}{nav('how-it-works.html', 'How It Works', 'how')}</nav>
  </div>
</header>
<main id="main" class="wrap">
{body}
</main>
<footer class="wrap foot">Questions? Email James at <a href="mailto:jabialek@syr.edu">jabialek@syr.edu</a>.</footer>
</div>
</body>
</html>
"""


def screen_html(i, total, s, wid):
    out = [f'<section class="screen" id="s{i}" aria-labelledby="h{i}">',
           f'<p class="step">Step {i + 1} of {total}</p>',
           f'<h2 id="h{i}" tabindex="-1">{e(s["title"])}</h2>']
    for p in s.get("paras", []):
        out.append(f"<p>{e(p)}</p>")
    if s.get("list"):
        out.append('<dl class="items">' + "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in s["list"]) + "</dl>")
    c = s.get("check")
    if c:
        name = f"{wid}-q{i}"
        opts = "".join(
            f'<label class="opt"><input type="radio" name="{name}" value="{k}"><span>{e(o)}</span></label>'
            for k, o in enumerate(c["options"]))
        out.append(f'<fieldset class="check" data-answer="{c["answer"]}"><legend>Quick check</legend>'
                   f'<p class="q">{e(c["q"])}</p>{opts}<p class="feedback" aria-live="polite"></p></fieldset>')
    out.append("</section>")
    return "\n".join(out)


def tables_screen(w):
    return {"title": "Your table this week",
            "paras": ["Tables are labeled 1 to 4 in the meeting room. Find your name and sit at your table. "
                      "Please arrive a few minutes before 8:30 PM so you're seated and ready to go."],
            "list": [[f"Table {i}", ", ".join(t)] for i, t in enumerate(w["tables"], 1)],
            "check": {"q": "When should you be seated at your table?",
                      "options": ["A few minutes before 8:30 PM", "Right at 8:30 PM", "Whenever you get there"],
                      "answer": 0}}


def week_body(w, latest):
    screens = ([tables_screen(w)] if w.get("tables") else []) + w["screens"]
    total = len(screens) + (1 if latest else 0)
    eyebrow = "This week" if latest else "Past week"
    parts = [f'<div class="week" data-week="{e(w["date"])}">',
             f'<p class="eyebrow">{eyebrow}</p><h1>{e(w["label"])}</h1>',
             f'<p class="meta">Read and complete by {e(site["confirm_by"])}</p>',
             f'<div class="progress" aria-hidden="true"><div class="bar"></div></div>',
             '<div class="screens">']
    for i, s in enumerate(screens):
        parts.append(screen_html(i, total, s, w["date"]))
    if latest:
        i = len(screens)
        if site.get("form_url"):
            action = (f'<a class="button" href="{e(site["form_url"])}" target="_blank" rel="noopener">'
                      'I’ve read this week’s Focus</a>'
                      '<p class="small">Opens a one-question form. Sign in with your SU account.</p>')
        else:
            action = '<p class="small">The confirmation link will appear here.</p>'
        parts.append(f"""<section class="screen final" id="s{i}" aria-labelledby="h{i}">
<p class="step">Step {i + 1} of {total}</p>
<h2 id="h{i}" tabindex="-1">You’re all set</h2>
<p>Last step: let me know you’ve read this week’s Focus. Please confirm by {e(site['confirm_by'])}.</p>
{action}
</section>""")
    parts.append('</div><div class="pager"><button type="button" class="back">Back</button>'
                 '<button type="button" class="next">Next</button></div></div>')
    return "\n".join(parts)


os.makedirs(os.path.join(ROOT, "weeks"), exist_ok=True)
for i, w in enumerate(weeks):
    with open(os.path.join(ROOT, "weeks", f'{w["date"]}.html'), "w") as f:
        f.write(page(w["label"], week_body(w, latest=(i == 0)), prefix="../",
                     current="this" if i == 0 else "archive", script=True))
if weeks:
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(page("This Week", week_body(weeks[0], latest=True), current="this", script=True))

rows = "".join(f'<li><a href="weeks/{w["date"]}.html">{e(w["label"])}</a></li>' for w in weeks)
with open(os.path.join(ROOT, "archive.html"), "w") as f:
    f.write(page("Past Weeks", f'<p class="eyebrow">Archive</p><h1>Past weeks</h1><ul class="archive">{rows}</ul>',
                 current="archive"))

how = f"""<p class="eyebrow">The basics</p><h1>How it works</h1>
<p class="lead">{e(site['name'])} is where our announcements live, so the team meeting can be about working together.</p>
<dl class="items">
<div><dt>Tuesday, 5:00 PM</dt><dd>A new Focus goes up. The PIN is in that week’s email.</dd></div>
<div><dt>By {e(site['confirm_by'])}</dt><dd>Go through each screen, answer the quick checks, and confirm at the end.</dd></div>
<div><dt>Wednesday</dt><dd>Team meeting. Questions about the Focus go to James by email, not the meeting.</dd></div>
</dl>
<h2 class="sub">The meeting</h2>
<p>How long it takes is up to all of us. Each agenda has a pace built in, and when we stay with it, we finish sooner.</p>
<dl class="items">
<div><dt>Warm-up</dt><dd>Led by an RA.</dd></div>
<div><dt>Building Check-In</dt><dd>What’s happening on our floors.</dd></div>
<div><dt>Developmental content</dt><dd>Something we learn together at our tables.</dd></div>
<div><dt>Challenge, recognition, questions</dt><dd>Quick ones to close.</dd></div>
<div><dt>Some weeks</dt><dd>A work session to prep for an upcoming event.</dd></div>
</dl>
<h2 class="sub">At your table</h2>
<p>Tables rotate three roles each week: a facilitator who keeps the conversation going, a timekeeper, and a reporter who shares with the room.</p>"""
with open(os.path.join(ROOT, "how-it-works.html"), "w") as f:
    f.write(page("How It Works", how, current="how"))
print("built", len(weeks), "week(s)")
