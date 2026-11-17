---
version: 1
slug: "public-admin-index-html"
primary_target: "public/admin/index.html"
related_targets: ["public/admin/admin.css","public/admin/admin.js"]
---

# Surface: admin (`/admin`, public/admin/index.html, admin.css, admin.js)

Mode: Operate. The owner, not a programmer, on a phone, adds and arranges photos and edits four text fields.

Task: upload several photos at once with per-photo progress; delete; drag to reorder; optional caption; edit name, subtitle, phone, WhatsApp. States: token not configured (Hebrew explanation, login closed), logged out, wrong token, rate-limited, uploading, upload error per file, empty gallery, 50-photo limit, saved, network error. Frequency: occasional, short sessions.

## Direction contract

THESIS: The back room of the same fashion house: the identical black-and-white world, used as a precise work surface. Refuses the generic dashboard (sidebar, cards, coloured status badges, icon buttons).

OWN-WORLD: Same tokens as the public page: white, black, one grey, Assistant only, 1 px black rules, square edges, no shadows, no icons except a drawn two-line drag grip. Status is text, never colour alone; errors are black text with a black rule, labelled "שגיאה".

STORY: The owner logs in once a month, taps "הוספת תמונות", picks from the camera roll, watches each row fill its progress bar, drags a photo to the top, fixes a caption, leaves.

FIRST VIEWPORT: Mobile: a top line with the site name and two text links (צפייה באתר, יציאה); a full-width black button "הוספת תמונות"; directly below, the photo list as rows (thumbnail, caption field, grip, delete). Texts form below the list.

FORM: Operate list editor in the public page's world (pinned by the same brief). seed: none (pinned). Signature interaction: press-and-drag the grip; the row lifts as a 1 px black outline and the others slide aside; order saves itself with a quiet "נשמר".

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
