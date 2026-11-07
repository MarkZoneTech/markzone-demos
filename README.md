# markzone-demos
Private website previews for prospective MarkZone clients, served at https://demo.markzonetech.com

- Each demo lives in its own folder: public/<client-slug>/index.html
  -> https://demo.markzonetech.com/<client-slug>/   (add ?lang=ar for Arabic)
- Every page is noindex (public/_headers + robots.txt), so demos never appear on Google.
- Add a demo: upload the new folder into public/ on GitHub -> Cloudflare redeploys automatically (about 1 minute).
- Remove a demo (unsold after ~30 days): delete its folder -> visitors see the 404 page.
- When a client buys: move the site to its own Worker/project with the client's domain.

## Live demos
| Client | Folder | Created |
|---|---|---|
| Dr. Emad Mosalam Eye Clinic (RAK) | dr-emad-mosalam | Sep 2026 |
| Dr. Suhad Obstetrics & Gynecology Clinic (RAK) | dr-suhad-rak | Nov 2026 (draft, not yet pushed) |

## Sample-site generator (templates + automatic picker)
Each prospect's sample site is built from `clients/<slug>.json` with ONE command; the template is chosen automatically from the business activity:

    python3 tools/build_site.py <slug>              # picks the template, writes public/<slug>/index.html
    python3 tools/pick_template.py <slug>           # just show which template would be used and why
    python3 tools/pick_template.py "Dental clinic"  # test any activity text
    python3 tools/pick_template.py --list           # list the templates
    python3 tools/screenshot.py <slug> <outdir>     # desktop / full page / mobile / Arabic screenshots

| Template | For |
|---|---|
| clinic | dental, medical, physio, eye, skin clinics |
| salon | salons, barbers, spas, nails, beauty |
| restaurant | restaurants, cafes, bakeries, sweets |
| retail | shops: electronics, fashion, tailoring, gifts, flowers, pharmacy |
| services | AC, plumbing, cleaning, garage, moving, laundry |
| fitness | gyms, yoga, martial arts, swimming, sports academies |
| education | nurseries, tuition, training centres, language, driving schools |
| general | anything else (fallback) |

How the pick works: keywords (English + Arabic) in `category` / `activity` / Google `types` / business name are scored; the best score wins, no match = `general`. To force one, add `"template": "salon"` to the client JSON (or run `build_site.py <slug> --template salon`).

Client JSON fields (same for all templates): slug, name_en/ar, area_en/ar, wa, phone_display, tel, rating, reviews, lead_en/ar, desc_en, address_en/ar, lat, lng, hours {open, close, days, by_day}, services [{en, ar, desc_en?, desc_ar?, price?}], category (used by the picker), optional brand {primary, accent} (derives the whole palette), optional show_prices (true = show service prices), optional copy {head_en, head_ar, sub_en, sub_ar, cta_en, cta_ar} to override hero wording.
Templates live in `templates/<name>/` (body.html + style.css) on top of `templates/_shared/` (base CSS, header, visit, footer, WhatsApp form script) and `templates/meta.json` (default palette, nav, hero wording). Sample clients for previewing each template: `clients/_samples/`.
