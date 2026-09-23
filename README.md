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
