#!/usr/bin/env python3
"""Build Mock (ur) Funeral guide pages from yeha/mock-ur-funeral/guides/*.md.

Run from the repo root:  python3 yeha/mock-ur-funeral/build.py
Writes mock-ur-funeral/guides/<slug>/index.html, the guides index, and sitemap.xml.
"""
import html
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "yeha" / "mock-ur-funeral" / "guides"
OUT = ROOT / "mock-ur-funeral" / "guides"
SITE = "https://" + (ROOT / "CNAME").read_text().strip()

CSS = """
:root{--blue:#4392F1;--amber:#F5B700;--brick:#D00000;--mint:#D5F9DE;--rouge:#E87EA1;--navy:#16233B;
--bg:var(--mint);--surface:#fff;--text:#16233B;--soft:#4A566E;--line:rgba(22,35,59,.14)}
@media (prefers-color-scheme:dark){:root{--bg:#0F1A2C;--surface:#18263D;--text:#EAFBEF;--soft:#A9B8CC;--line:rgba(234,251,239,.16)}}
*{box-sizing:border-box}html,body{margin:0}
body{background:var(--bg);color:var(--text);font:17px/1.65 'Work Sans',system-ui,-apple-system,sans-serif;-webkit-font-smoothing:antialiased}
.stripe{height:8px;background:linear-gradient(90deg,var(--blue) 0 25%,var(--amber) 25% 50%,var(--brick) 50% 75%,var(--rouge) 75% 100%)}
nav{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:10px 18px;border-bottom:1px solid var(--line)}
nav a{color:inherit;text-decoration:none;font-weight:600}
.mark{font-family:'Fraunces',Georgia,serif;font-weight:900}
main{max-width:720px;margin:0 auto;padding:28px 20px 48px}
.eyebrow{font:500 .8rem 'IBM Plex Mono',monospace;letter-spacing:.08em;text-transform:uppercase;color:var(--soft)}
h1,h2{font-family:'Fraunces',Georgia,serif;line-height:1.15}
h1{font-size:clamp(1.9rem,6vw,2.7rem);margin:.3em 0 .5em}h2{font-size:1.4rem;margin-top:1.8em}
a{color:inherit}
.card{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:18px 20px;margin:14px 0}
.card h2{margin:0 0 .3em;font-size:1.2rem}.card p{margin:0;color:var(--soft)}
.btn{display:inline-block;background:var(--amber);color:#16233B;font-weight:700;text-decoration:none;padding:12px 20px;border-radius:999px;margin-top:10px}
footer{text-align:center;color:var(--soft);font-size:.85rem;padding:24px 18px 32px}
:focus-visible{outline:3px solid var(--amber);outline-offset:3px}
"""

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{title} · Golden Soul Circus</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,700;9..144,900&family=Work+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
<div class="stripe" aria-hidden="true"></div>
<nav><a class="mark" href="/">Golden Soul Circus</a><a href="/mock-ur-funeral/#book">Book →</a></nav>
<main>
{body}
</main>
<footer>Sacred and silly. Both, always. · Golden Soul Circus, Nashville, TN<br>
Mock (ur) Funeral sessions are ceremony and education, not medical care or therapy.</footer>
<div class="stripe" aria-hidden="true"></div>
</body>
</html>
"""


def parse(path):
    text = path.read_text()
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    if not m:
        sys.exit(f"{path.name}: missing front matter")
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    for key in ("title", "description", "date"):
        if not meta.get(key):
            sys.exit(f"{path.name}: front matter needs {key}")
    meta["slug"] = path.stem
    meta["body"] = m.group(2)
    return meta


def main():
    guides = sorted((parse(p) for p in SRC.glob("*.md")), key=lambda g: g["date"], reverse=True)
    OUT.mkdir(parents=True, exist_ok=True)
    for g in guides:
        url = f"{SITE}/mock-ur-funeral/guides/{g['slug']}/"
        body = (
            f'<p class="eyebrow"><a href="/mock-ur-funeral/guides/">Mock (ur) Funeral guides</a></p>\n'
            f"<h1>{html.escape(g['title'])}</h1>\n"
            + markdown.markdown(g["body"])
            + '\n<p><a class="btn" href="/mock-ur-funeral/#book">Book a Mock (ur) Funeral · $250</a></p>'
        )
        d = OUT / g["slug"]
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(PAGE.format(
            title=html.escape(g["title"]), desc=html.escape(g["description"], quote=True),
            url=url, css=CSS, body=body))
    cards = "\n".join(
        f'<div class="card"><h2><a href="/mock-ur-funeral/guides/{g["slug"]}/">{html.escape(g["title"])}</a></h2>'
        f'<p>{html.escape(g["description"])}</p></div>' for g in guides)
    idx_body = ('<p class="eyebrow">Golden Soul Circus</p>\n<h1>Mock (ur) Funeral ideas &amp; guides</h1>\n'
                '<p>Birthdays, retirements, team offsites and other goodbyes to an old version of yourself, '
                'hosted by hospice nurses in Nashville.</p>\n' + cards +
                '\n<p><a class="btn" href="/mock-ur-funeral/#book">Book a Mock (ur) Funeral · $250</a></p>')
    (OUT / "index.html").write_text(PAGE.format(
        title="Mock (ur) Funeral ideas &amp; guides",
        desc="Ideas for living-funeral parties: milestone birthdays, retirements and team events in Nashville.",
        url=f"{SITE}/mock-ur-funeral/guides/", css=CSS, body=idx_body))

    pages = sorted(p for p in ROOT.rglob("index.html")
                   if ".git" not in p.parts and "yeha" not in p.parts and "full-" not in str(p))
    urls = []
    for p in pages:
        rel = p.parent.relative_to(ROOT).as_posix()
        urls.append(f"{SITE}/" if rel == "." else f"{SITE}/{rel}/")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    print(f"built {len(guides)} guide(s), {len(urls)} sitemap urls")


if __name__ == "__main__":
    main()
