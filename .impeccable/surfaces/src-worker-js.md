---
version: 1
slug: "src-worker-js"
primary_target: "src/worker.js"
related_targets: ["public/site.css","public/site.js"]
---

# Surface: public gallery (`/`, rendered by src/worker.js, styled by public/site.css, behavior in public/site.js)

Mode: Experience. The photographs lead from the first viewport; the interface recedes.

Audience and job: Hebrew-speaking guests on a phone, arriving from a shared link, deciding whether to book. Action: call or WhatsApp the owner. Content: title, subtitle, gallery (up to 50 photos, optional captions), phone, WhatsApp. Nothing else (confirmed).

## Direction contract

THESIS: A zimmer presented like a high-end fashion house presents a collection: the place is the garment, the photographs are the lookbook. Refuses the category default of a hero slider over amenity icons, testimonial cards and a booking widget.

OWN-WORLD: Pure white ground, pure black ink, one hairline grey for image placeholders. No accent colour, no shadows, no radii, no icons. Small, exact sans text (Assistant) at 12–14 px with open tracking; the name set in a fine high-contrast display face (Bellefair). Controls are words, underlined or boxed in 1 px black.

STORY: The guest sees the place before reading anything, scrolls the collection at full width, opens any photo into a white full-screen view, then taps WhatsApp or call, which are always one thumb-reach away.

FIRST VIEWPORT: Mobile: a slim header (name centred, small; subtitle beneath), then the lead photograph edge to edge filling the rest of the viewport. A fixed two-part bar at the bottom: WhatsApp (black) and call (white, 1 px black). Desktop: the same header, lead image full-bleed to about 80 vh, contact as words at the header's edge.

FORM: Fashion-store lookbook grid (pinned by the user's brief: "the minimalism of a high-end fashion store: white background, generous empty space, large photography leading the page, small precise typography, black and white with no accent colors, no shadows, no rounded corners, no decorative icons"). seed: none (pinned). Signature interaction: tapping a photo morphs it into the white full-screen viewer (View Transitions where supported), swipe or arrow keys to move, a quiet "3 / 24" counter. Motion grammar: images fade up from the placeholder grey on load, 400 ms exponential ease-out; nothing else moves.

FINISH: unreviewed and undocumented is unfinished; this build ends with the finish review, the verdict, DESIGN.md, and every shipping raster carrying its provenance
