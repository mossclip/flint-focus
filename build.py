"""Build The Flint Focus from content/*.json.  Run: python3 build.py"""
import json, glob, os, html
from urllib.parse import quote

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
    if s.get("link"):
        out.append(f'<p><a class="button" href="{e(s["link"]["href"])}" target="_blank" rel="noopener">{e(s["link"]["text"])}</a></p>')
    if s.get("list"):
        out.append('<dl class="items">' + "".join(f"<div><dt>{e(a)}</dt><dd>{e(b)}</dd></div>" for a, b in s["list"]) + "</dl>")
    for p in s.get("after", []):
        out.append(f"<p>{e(p)}</p>")
    c = s.get("check")
    if c and c.get("type") == "pick":
        sels = "".join(
            f'<label class="pick"><span>{e(f["label"])}</span><select data-answer="{e(f["answer"])}">'
            '<option value="">Choose</option>' + "".join(f'<option>{e(o)}</option>' for o in f["options"]) + '</select></label>'
            for f in c["fields"])
        out.append(f'<fieldset class="check picked"><legend>Say it back</legend><p class="q">{e(c["q"])}</p>'
                   f'<div class="picks">{sels}</div><button type="button" class="typed-go">Check</button>'
                   '<p class="feedback" aria-live="polite"></p></fieldset>')
    elif c and c.get("type") == "text":
        name = f"{wid}-q{i}"
        out.append(f'<fieldset class="check typed" data-patterns="{e(json.dumps(c["patterns"]))}"><legend>Say it back</legend>'
                   f'<p class="q">{e(c["q"])}</p>'
                   f'<label class="sr" for="{name}">Your answer</label>'
                   f'<input class="typed-in" id="{name}" type="text" autocomplete="off" placeholder="{e(c.get("placeholder", ""))}">'
                   f'<button type="button" class="typed-go">Check</button><p class="feedback" aria-live="polite"></p></fieldset>')
    elif c:
        name = f"{wid}-q{i}"
        opts = "".join(
            f'<label class="opt"><input type="radio" name="{name}" value="{k}"><span>{e(o)}</span></label>'
            for k, o in enumerate(c["options"]))
        ans = ",".join(map(str, c["answer"])) if isinstance(c["answer"], list) else str(c["answer"])
        fbs = f' data-feedback="{e(json.dumps(c["feedback"]))}"' if c.get("feedback") else ""
        out.append(f'<fieldset class="check" data-answer="{ans}"{fbs}><legend>{e(c.get("legend", "Quick check"))}</legend>'
                   f'<p class="q">{e(c["q"])}</p>{opts}<p class="feedback" aria-live="polite"></p></fieldset>')
    out.append("</section>")
    return "\n".join(out)


def tables_screen(w):
    return {"title": "Your table this week",
            "paras": ["Tables are labeled 1 to 4 in the meeting room. Find your name and sit at your table. Take note of it."],
            "after": ["If you can, try to come 5 to 10 minutes early. Get settled, get your pencil out, catch your breath, run to the "
                      "bathroom. Just get parked so you're ready to work and engage when we start. If you have class right before and "
                      "have to rush over, I totally understand. Please just be safe."],
            "list": [[f"Table {i}", ", ".join(n + (" (excused this week, honorary member)" if n in w.get("excused", []) else "") for n in t)] for i, t in enumerate(w["tables"], 1)],
            "check": {"q": "If you can, when should you get to the meeting?",
                      "options": ["5 to 10 minutes early", "Right on time", "Whenever you get there"],
                      "answer": 0}}


def week_body(w, latest):
    screens = w["screens"][:1] + ([tables_screen(w)] if w.get("tables") else []) + w["screens"][1:]
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
        code = w.get("code", "")
        mail = ("mailto:jabialek@syr.edu?subject=" +
                quote(f"Flint Focus {w['label']}: {code}") + "&body=" + quote(f"Code: {code}"))
        parts.append(f"""<section class="screen final" id="s{i}" aria-labelledby="h{i}">
<p class="step">Step {i + 1} of {total}</p>
<h2 id="h{i}" tabindex="-1">You’re all set. Here’s your code.</h2>
<p class="code">{e(code)}</p>
<p>Email this code to James by {e(site['confirm_by'])}. That’s how he marks you as done for the week.</p>
<p><strong>This is mandatory.</strong> The Flint Focus is part of our team meeting, so completing it counts the same as showing up.</p>
<a class="button" href="{e(mail)}">Email James the code</a>
<p class="small">Opens a new email to jabialek@syr.edu with the code filled in. Or just send it yourself.</p>
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
<div><dt>By {e(site['confirm_by'])}</dt><dd>Go through each screen and answer the quick checks. At the end you’ll get a two-word code. Email it to James. This is mandatory.</dd></div>
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
<p>Tables change every week. Your table is on the second screen of each week’s Flint Focus.</p>"""
with open(os.path.join(ROOT, "how-it-works.html"), "w") as f:
    f.write(page("How It Works", how, current="how"))
print("built", len(weeks), "week(s)")
