#!/usr/bin/env python3
"""Build a bilingual clinic sample site from clients/<slug>.json -> public/<slug>/index.html"""
import json, sys, html, urllib.parse, colorsys, re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DAYS = [("Sunday","الأحد"),("Monday","الاثنين"),("Tuesday","الثلاثاء"),("Wednesday","الأربعاء"),("Thursday","الخميس"),("Friday","الجمعة"),("Saturday","السبت")]
AR_DIGITS = str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩")


def _rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def _hex(r,g,b): return "#%02x%02x%02x" % tuple(max(0,min(255,round(v*255))) for v in (r,g,b))
def _shift(h, l=None, s=None, dl=0.0):
    hh,ll,ss = colorsys.rgb_to_hls(*_rgb(h))
    ll = l if l is not None else max(0,min(1,ll+dl))
    ss = s if s is not None else ss
    return _hex(*colorsys.hls_to_rgb(hh,ll,ss))
def _lum(h):
    r,g,b=[(c/12.92 if c<=0.03928 else ((c+0.055)/1.055)**2.4) for c in _rgb(h)]
    return 0.2126*r+0.7152*g+0.0722*b
def palette_from_brand(brand, base):
    """Derive the full clinic palette from the clinic's own primary (+ optional accent) colour."""
    pri = brand["primary"]
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", pri): raise SystemExit("bad primary colour")
    hh,ll,ss = colorsys.rgb_to_hls(*_rgb(pri))
    # keep the brand hue; force enough depth so white text stays readable on it
    primary = _shift(pri, l=min(ll,0.30))
    p2 = _shift(pri, l=min(max(ll,0.30),0.40))
    night = _shift(pri, l=0.13, s=min(ss,0.6))
    acc = brand.get("accent") or base["accent"]
    if _lum(acc) < 0.18: acc = _shift(acc, l=0.55)   # accent sits on dark backgrounds, so keep it light enough
    out = dict(base)
    out.update(night=night, primary=primary, primary2=p2, accent=acc,
               accent_soft=_shift(acc, l=0.88), ink=_shift(pri, l=0.12, s=min(ss,0.35)),
               paper=_shift(pri, l=0.97, s=min(ss,0.3)), line=_shift(pri, l=0.89, s=min(ss,0.25)),
               muted=_shift(pri, l=0.40, s=min(ss,0.15)))
    return out

def ar_time(t):
    return t.replace("AM","ص").replace("PM","م").translate(AR_DIGITS)

def build(slug):
    c = json.loads((ROOT/"clients"/f"{slug}.json").read_text(encoding="utf-8"))
    p = palette_from_brand(c["brand"], c["palette"]) if c.get("brand",{}).get("primary") else c["palette"]; e = html.escape
    t = (ROOT/"templates"/"clinic.html").read_text(encoding="utf-8")
    css = (ROOT/"templates"/"clinic.css").read_text(encoding="utf-8")
    h = c["hours"]
    per = h.get("by_day")  # optional per-day override: {"4": "1:00 PM – 10:00 PM"}
    hours = [{"en":en,"ar":ar,"t":((per or {}).get(str(i)) or (f'{h["open"]} – {h["close"]}' if i in h["days"] else "Closed"))} for i,(en,ar) in enumerate(DAYS)]
    for x in hours: x["t"] = x["t"]
    svc_json = [{"en":s["en"],"ar":s["ar"]} for s in c["services"]]
    q = urllib.parse.quote(f'{c["name_en"]} {", ".join(c["address_en"])}')
    rep = {
      "CSS": css, "SLUG": c["slug"],
      "NAME_EN": e(c["name_en"]), "NAME_AR": e(c["name_ar"]),
      "AREA_EN": e(c["area_en"]), "AREA_AR": e(c["area_ar"]),
      "DESC_EN": e(c["desc_en"]), "LEAD_EN": e(c["lead_en"]), "LEAD_AR": e(c["lead_ar"]),
      "TEL": c["tel"], "WA": c["wa"], "PHONE_DISPLAY": c["phone_display"],
      "RATING": c["rating"], "REVIEWS": c["reviews"], "OPEN_DAYS": str(len(h["days"])),
      "PRIMARY_URL": p["primary"].replace("#","%23"),
      "NIGHT": p["night"], "PRIMARY": p["primary"], "PRIMARY2": p["primary2"],
      "ACCENT": p["accent"], "ACCENT_SOFT": p["accent_soft"], "INK": p["ink"],
      "PAPER": p["paper"], "LINE": p["line"], "MUTED": p["muted"],
      "SERVICES_LI_EN": "".join(f"<li>{e(s['en'])}</li>" for s in c["services"]),
      "SERVICES_LI_AR": "".join(f"<li>{e(s['ar'])}</li>" for s in c["services"]),
      "ADDR_EN_INLINE": e(", ".join(c["address_en"])), "ADDR_AR_INLINE": e("، ".join(c["address_ar"])),
      "ADDR_EN_BR": "<br>".join(e(x) for x in c["address_en"]),
      "ADDR_AR_BR": "<br>".join(e(x) for x in c["address_ar"]),
      "DIRECTIONS_URL": f'https://www.google.com/maps/search/?api=1&query={q}',
      "MAP_EMBED": f'https://www.google.com/maps?q={c["lat"]},{c["lng"]}&z=16&output=embed',
      "HOURS_JSON": json.dumps(hours, ensure_ascii=False),
      "SERVICES_JSON": json.dumps(svc_json, ensure_ascii=False),
    }
    for k,v in rep.items(): t = t.replace(f"<<{k}>>", v)
    assert "<<" not in t.replace("<<<","") or True
    left = [s for s in __import__("re").findall(r"<<[A-Z_]+>>", t)]
    if left: sys.exit(f"Unreplaced placeholders: {set(left)}")
    out = ROOT/"public"/c["slug"]; out.mkdir(parents=True, exist_ok=True)
    (out/"index.html").write_text(t, encoding="utf-8")
    print("built", out/"index.html", len(t), "bytes")

if __name__ == "__main__":
    build(sys.argv[1])
