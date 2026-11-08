#!/usr/bin/env python3
"""Pick the site template that fits a business's activity.
Usage: pick_template.py <slug>            (reads clients/<slug>.json)
       pick_template.py "Dental clinic"   (any free text: activity / category / name)
       pick_template.py --list
Looks at: client.template (manual override) > category/activity/types/name keywords (English + Arabic). Falls back to 'general'."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT/"templates"/"meta.json").read_text(encoding="utf-8"))
RULES = {
 "clinic": "clinic dental dentist dentistry orthodont medical medicine doctor physician hospital physiotherapy physio dermatolog ophthalm optometr eye care paediatric pediatric gynecolog obstetric cardiolog dialysis polyclinic health center health centre radiology laborator عيادة اسنان أسنان طبي طبية مستشفى طبيب علاج طبيعي مختبر مركز صحي جلدية عيون نساء وولادة",
 "salon": "salon beauty barber barbershop hairdress hair stylist spa nail lashes eyebrow makeup make-up massage waxing threading grooming henna tanning صالون تجميل حلاق حلاقة كوافير سبا مساج أظافر رموش مكياج حناء عناية بالبشرة",
 "restaurant": "restaurant cafe café coffee bakery shawarma grill pizza burger catering sweets dessert juice kitchen kebab biryani buffet bistro diner roastery ice cream chocolate food truck مطعم كافيه مقهى كوفي مخبز شاورما مشاوي حلويات عصائر كيك مطبخ بيتزا برجر وجبات",
 "retail": "shop store boutique electronics mobile phone supermarket grocery fashion clothing garment tailor tailoring abaya gift flower florist furniture perfume oud jewellery jewelry stationery pharmacy optical toys bookstore carpet textile fabric mart trading محل متجر الكترونيات إلكترونيات جوالات ملابس خياط خياطة عبايات هدايا زهور ورد أثاث عطور عود مجوهرات ذهب قرطاسية صيدلية بقالة سوبرماركت أقمشة تجارة",
 "services": "repair maintenance air conditioning ac service plumbing plumber electrician electrical cleaning laundry dry clean car wash garage auto workshop towing moving mover relocation pest control carpentry painting contracting gypsum glass aluminium aluminum handyman waterproofing landscaping sanitary تكييف صيانة سباكة سباك كهربائي كهرباء تنظيف مغسلة غسيل سيارات كراج ورشة سطحة نقل أثاث مكافحة حشرات نجارة دهان مقاولات جبس زجاج المنيوم ألمنيوم",
 "curtains": "curtain curtains blind blinds drape drapes drapery roller blind roller blinds sheer sheers window treatment window treatments window dressing curtain maker curtain supplier curtain shop ستائر ستاير برادي ستارة بلايند ستائر وبرادي تفصيل ستائر",
 "decor": "decor decors decoration decorations decorator decorators finishing wallpaper wall panel wall panels false ceiling gypsum board cladding home decor ديكور ديكورات تشطيب تشطيبات تصميم داخلي ورق جدران ديكور داخلي جبس بورد",
 "interior": "interior interiors interior design interior designer interior designers interior architect interior architecture fit-out fitout fit out joinery contracting interior contractor  تصميم داخلي مصمم داخلي  مقاولات تشطيب وتصميم",
 "events": "event events event planner event planning event styling event organizer event organiser wedding weddings wedding planner wedding services wedding hall kosha koosha engagement party parties birthday henna balloon balloons party supplies celebration occasion occasions تنظيم حفلات تنظيم مناسبات مناسبات أفراح افراح كوش كوشات زفاف حفلات حنة بالونات تنسيق حفلات تنسيق مناسبات",
 "nursery": "nursery nurseries kindergarten preschool pre-school day care daycare childcare child care playgroup early years early learning early childhood نيرسري حضانة حضانات روضة رياض أطفال رعاية أطفال",
 "fitness": "gym fitness yoga pilates crossfit martial arts karate taekwondo boxing judo swimming swim sports academy football academy sports club personal training trainer zumba dance studio gymnastics نادي رياضي صالة رياضية جيم لياقة يوغا بيلاتس كاراتيه تايكوندو ملاكمة سباحة أكاديمية رياضية كرة قدم تدريب شخصي",
 "education": "school tuition tutor tutoring training centre training center institute academy language course courses driving school learning center learning centre coaching music lessons quran مدرسة معهد مركز تدريب دروس تقوية تعليم تعليمي دورات سواقة لغات أكاديمية تحفيظ",
 "legal": "law firm law firms lawyer lawyers attorney advocate advocates legal consultant legal consultancy legal consultants legal services notary arbitration litigation barrister solicitor محاماة محامي محامون مستشار قانوني استشارات قانونية مكتب محاماة قانون قانونية موثق كاتب عدل تحكيم",
 "general": "office consultant consulting consultancy agency real estate property accounting audit travel tourism printing photography events wedding planner insurance advertising marketing it services software cleaning company تأجير عقارات مكتب استشارات محاماة محاسبة سفر سياحة طباعة تصوير تأمين دعاية",
}
# multi-word phrases are split on 2+ spaces? No: we keep a phrase list by pulling known phrases back together.
PHRASES = ["air conditioning","car wash","dry clean","pest control","real estate","martial arts","sports academy","football academy","personal training","day care","child care","early years","early learning","early childhood","pre-school","driving school","training centre","training center","learning center","learning centre","language course","health center","health centre","eye care","ice cream","food truck","sports club","dance studio","it services","law firm","law firms","legal consultant","legal consultancy","legal consultants","legal services","مكتب محاماة","مستشار قانوني","استشارات قانونية","كاتب عدل","event planner","event planning","event styling","event organizer","event organiser","wedding planner","wedding services","wedding hall","interior design","interior designer","interior designers","interior architect","interior architecture","interior contractor","window treatment","window treatments","window dressing","curtain maker","curtain supplier","curtain shop","roller blind","roller blinds","مصمم داخلي","ستائر وبرادي","تفصيل ستائر","fit out","wall panel","wall panels","false ceiling","gypsum board","home decor","party supplies","تنظيم حفلات","تنظيم مناسبات","تنسيق حفلات","تنسيق مناسبات","تصميم داخلي","ورق جدران","ديكور داخلي","جبس بورد","cleaning company","ac service","make-up","مركز صحي","رياض أطفال","رعاية أطفال","علاج طبيعي","نساء وولادة","عناية بالبشرة","كرة قدم","مركز تدريب","تدريب شخصي","أكاديمية رياضية","نادي رياضي","صالة رياضية","مكافحة حشرات","غسيل سيارات","نقل أثاث","سواقة"]
def _kw(text):
    words, out = text.split(), []
    t = " " + " ".join(words) + " "
    for ph in PHRASES:
        if f" {ph} " in t: out.append(ph); t = t.replace(f" {ph} ", " ")
    out += t.split()
    return out
KW = {k:_kw(v) for k,v in RULES.items()}
ORDER = list(RULES)
def _match(kw, text):
    if re.search(r"[a-z]", kw): return re.search(r"(?<![a-z])"+re.escape(kw)+r"(s|es)?(?![a-z])", text) is not None
    return kw in text
def pick(c):
    """c: dict (client json) or str. Returns (template, score, reasons)."""
    if isinstance(c, str): c = {"category": c}
    if c.get("template") in META or c.get("template") == "clinic": return c["template"], 99, ["set manually in client json"]
    fields = [c.get("activity",""), c.get("category",""), " ".join(c.get("types",[]) or []).replace("_"," "), c.get("name_en",""), c.get("name_ar","")]
    weights = [3, 3, 2, 1, 1]
    scores = {k:0 for k in KW}; why = {k:[] for k in KW}
    for f, w in zip(fields, weights):
        f = (f or "").lower()
        for k, kws in KW.items():
            for kw in kws:
                if _match(kw, f): scores[k] += w*max(1, len(kw)//4); why[k].append(kw)
    best = max(ORDER, key=lambda k:(scores[k], -ORDER.index(k)))
    if scores[best] == 0: return "general", 0, ["no activity keyword matched: using the general template"]
    return best, scores[best], sorted(set(why[best]))
if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: sys.exit(__doc__)
    if a[0] == "--list":
        print("clinic: Clinics & health (dental, medical, physio, eye, skin)")
        for k, m in META.items(): print(f"{k}: {m['label']}")
        sys.exit()
    p = ROOT/"clients"/f"{a[0]}.json"
    c = json.loads(p.read_text(encoding="utf-8")) if p.exists() else " ".join(a)
    t, s, r = pick(c); print(f"{t}  (score {s}; matched: {', '.join(r)})")
