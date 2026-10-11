#!/usr/bin/env python3
"""Build a bilingual clinic sample site from clients/<slug>.json -> public/<slug>/index.html"""
import json, sys, html, urllib.parse
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
DAYS = [("Sunday","الأحد"),("Monday","الاثنين"),("Tuesday","الثلاثاء"),("Wednesday","الأربعاء"),("Thursday","الخميس"),("Friday","الجمعة"),("Saturday","السبت")]
AR_DIGITS = str.maketrans("0123456789","٠١٢٣٤٥٦٧٨٩")

def ar_time(t):
    return t.replace("AM","ص").replace("PM","م").translate(AR_DIGITS)

def build(slug):
    c = json.loads((ROOT/"clients"/f"{slug}.json").read_text(encoding="utf-8"))
    p = c["palette"]; e = html.escape
    t = (ROOT/"templates"/"clinic.html").read_text(encoding="utf-8")
    css = (ROOT/"templates"/"clinic.css").read_text(encoding="utf-8")
    h = c["hours"]
    hours = [{"en":en,"ar":ar,"t":(f'{h["open"]} – {h["close"]}' if i in h["days"] else "Closed")} for i,(en,ar) in enumerate(DAYS)]
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
