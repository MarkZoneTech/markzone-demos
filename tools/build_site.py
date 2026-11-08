#!/usr/bin/env python3
"""Build a bilingual sample site from clients/<slug>.json, choosing the template automatically.
Usage: build_site.py <slug> [--template NAME] [--out DIR]
Template order: --template > client.template > pick_template.py (activity keywords) > general.
Output: public/<slug>/index.html (or DIR/<slug>/index.html)."""
import json, sys, html, urllib.parse, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_clinic import palette_from_brand, DAYS
import build_clinic
from pick_template import pick, META
ROOT = Path(__file__).resolve().parent.parent
T = ROOT/"templates"
e = html.escape

def rd(p): return Path(p).read_text(encoding="utf-8")

def fill(t, rep):
    for k, v in rep.items(): t = t.replace(f"<<{k}>>", v)
    return t

def build(slug, template=None, out_root=None):
    c = json.loads(rd(ROOT/"clients"/f"{slug}.json"))
    tpl, score, why = (template, 99, ["--template"]) if template else pick(c)
    if tpl == "clinic":
        build_clinic.build(slug, out_root); print("template: clinic", f"({', '.join(why)})"); return tpl
    m = META[tpl]
    base = m["palette"]
    if c.get("brand", {}).get("primary"): p = palette_from_brand(c["brand"], base)
    elif c.get("palette") and c.get("template") == tpl: p = c["palette"]
    else: p = base
    copy = {**m["copy"], **c.get("copy", {})}
    h = c["hours"]; per = h.get("by_day") or {}
    hours = [{"en":en,"ar":ar,"t":per.get(str(i)) or (f'{h["open"]} – {h["close"]}' if i in h["days"] else "Closed")} for i,(en,ar) in enumerate(DAYS)]
    show_price = bool(c.get("show_prices"))
    cards, rows = [], []
    for i, s in enumerate(c["services"], 1):
        d_en, d_ar, pr = s.get("desc_en", ""), s.get("desc_ar", ""), (s.get("price") if show_price else "")
        cards.append(f'<div class="card rv"><i>{i:02d}</i><h3 class="en">{e(s["en"])}</h3><h3 class="ar">{e(s["ar"])}</h3>'
                     + (f'<p class="en">{e(d_en)}</p><p class="ar">{e(d_ar)}</p>' if d_en else "")
                     + (f'<span class="price" dir="ltr">{e(pr)}</span>' if pr else "") + "</div>")
        rows.append(f'<li class="rv"><span class="nm"><b class="en">{e(s["en"])}</b><b class="ar">{e(s["ar"])}</b>'
                    + (f'<small class="en">{e(d_en)}</small><small class="ar">{e(d_ar)}</small>' if d_en else "") + '</span>'
                    + (f'<span class="dots"></span><span class="pr" dir="ltr">{e(pr)}</span>' if pr else "") + "</li>")
    nav = "".join(f'<a href="#{n["href"]}"><span class="en">{n["en"]}</span><span class="ar">{n["ar"]}</span></a>' for n in m["nav"])
    q = urllib.parse.quote(f'{c["name_en"]} {", ".join(c["address_en"])}')
    mono = next((ch for ch in c["name_en"] if ch.isalnum()), "M").upper()
    rep = {
      "SLUG": c["slug"], "NAME_EN": e(c["name_en"]), "NAME_AR": e(c["name_ar"]), "AREA_EN": e(c["area_en"]), "AREA_AR": e(c["area_ar"]),
      "DESC_EN": e(c["desc_en"]), "LEAD_EN": e(c["lead_en"]), "LEAD_AR": e(c["lead_ar"]),
      "TEL": c["tel"], "WA": c["wa"], "PHONE_DISPLAY": c["phone_display"], "RATING": c["rating"], "REVIEWS": c["reviews"],
      "OPEN_DAYS": str(len(h["days"])),
      "OPEN_LINE_EN": (f'Open {len(h["days"])} days a week, see the hours below' if h["days"] else "Ask us for the opening hours"),
      "OPEN_LINE_AR": (f'مفتوحين {len(h["days"])} أيام في الأسبوع، شوفوا الأوقات تحت' if h["days"] else "اسألونا عن أوقات الدوام"), "MONO": e(mono), "NAV": nav,
      "PRIMARY_URL": p["primary"].replace("#","%23"), "ACCENT_URL": p["accent"].replace("#","%23"),
      "NIGHT": p["night"], "PRIMARY": p["primary"], "PRIMARY2": p["primary2"], "ACCENT": p["accent"], "ACCENT_SOFT": p["accent_soft"],
      "INK": p["ink"], "PAPER": p["paper"], "LINE": p["line"], "MUTED": p["muted"],
      "SERVICE_CARDS": "".join(cards), "MENU_ROWS": "".join(rows),
      "SERVICES_LI_EN": "".join(f"<li>{e(s['en'])}</li>" for s in c["services"]),
      "SERVICES_LI_AR": "".join(f"<li>{e(s['ar'])}</li>" for s in c["services"]),
      "ADDR_EN_INLINE": e(", ".join(c["address_en"])), "ADDR_AR_INLINE": e("، ".join(c["address_ar"])),
      "ADDR_EN_BR": "<br>".join(e(x) for x in c["address_en"]), "ADDR_AR_BR": "<br>".join(e(x) for x in c["address_ar"]),
      "DIRECTIONS_URL": f'https://www.google.com/maps/search/?api=1&query={q}',
      "MAP_EMBED": f'https://www.google.com/maps?q={c["lat"]},{c["lng"]}&z=16&output=embed',
      "HOURS_JSON": json.dumps(hours, ensure_ascii=False),
      "SERVICES_JSON": json.dumps([{"en":s["en"],"ar":s["ar"]} for s in c["services"]], ensure_ascii=False),
    }
    for k, v in copy.items(): rep["C_"+k.upper()] = e(v)
    css = rd(T/"_shared"/"base.css") + "\n" + rd(T/tpl/"style.css")
    head = f'''<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title><<NAME_EN>> | <<AREA_EN>></title>
<meta name="description" content="<<DESC_EN>>">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='24' fill='<<PRIMARY_URL>>'/><circle cx='50' cy='50' r='20' fill='<<ACCENT_URL>>'/></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@300;400;500;600;700&family=IBM+Plex+Sans+Arabic:wght@300;400;500;600;700&family=IBM+Plex+Serif:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
{css}
:root{{--night:<<NIGHT>>;--primary:<<PRIMARY>>;--primary-2:<<PRIMARY2>>;--gold:<<ACCENT>>;--gold-soft:<<ACCENT_SOFT>>;--ink:<<INK>>;--paper:<<PAPER>>;--line:<<LINE>>;--muted:<<MUTED>>}}
</style>
</head>
<body>
'''
    page = (head + rd(T/"_shared"/"header.html") + '<main id="top">\n' + rd(T/tpl/"body.html") + '\n</main>\n'
            + rd(T/"_shared"/"visit.html") + rd(T/"_shared"/"footer.html") + rd(T/"_shared"/"script.html") + "\n</body>\n</html>\n")
    import re
    if c.get("hide_rating"): page = re.sub(r'<div class="rating[^>]*>.*?</div>', '', page, flags=re.S)
    page = fill(page, rep)
    left = set(re.findall(r"<<[A-Z_]+>>", page))
    if left: sys.exit(f"Unreplaced placeholders: {left}")
    out = Path(out_root or ROOT/"public")/c["slug"]; out.mkdir(parents=True, exist_ok=True)
    (out/"index.html").write_text(page, encoding="utf-8")
    print(f"template: {tpl} ({', '.join(why)}) -> built {out/'index.html'} ({len(page)} bytes)")
    return tpl

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("slug"); ap.add_argument("--template"); ap.add_argument("--out")
    a = ap.parse_args(); build(a.slug, a.template, a.out)
