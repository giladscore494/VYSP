# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Pinned by the owner's brief: one Cloudflare Worker with static assets and one R2 bucket binding. No database, no framework, no external services, no build step. Plain HTML, CSS and vanilla JavaScript. Must fit the Cloudflare free plan (10 ms CPU per request), so no server-side image processing. Deployed by Workers Builds on push to `main`.

## Users

- **Guests (primary audience of the public page):** Hebrew-speaking Israelis deciding where to stay for a short getaway, mostly arriving on a phone from a link (WhatsApp, Instagram, a listing site). Their job: see what the place really looks like, then call or message the owner.
- **The owner (sole user of /admin):** runs a small zimmer and is not a programmer. Does every routine action from a phone: adds photos straight from the camera roll, removes or reorders them, writes captions, and edits the name, subtitle, phone and WhatsApp number.

## Product Purpose

A single-page photo gallery for one zimmer, whose photographs do the selling. Success: a guest scrolls the photos, gets a true sense of the place, and taps call or WhatsApp; the owner keeps the site current without help and without touching code or the Cloudflare dashboard after the one-time setup.

## Positioning

Not a booking platform and not a listing: the owner's own site, where full-resolution photographs lead and nothing competes with them.

## Operating Context

- Owner uploads phone photos (often 5–15 MB HEIC-converted JPEGs) over mobile data; the admin browser makes 800 px and 2000 px WebP variants before upload, and the untouched original is kept.
- All state lives in R2: image files and one `site.json` (photo order, captions, site texts).
- Up to 50 photos.
- ADMIN_TOKEN is set once as a Secret in the Cloudflare dashboard; until then /admin explains (in Hebrew) that login is closed.

## Capabilities and Constraints

- Public: Hebrew, RTL, mobile first. One page: title, subtitle, gallery with lightbox, lazy loading and srcset, phone and WhatsApp contact.
- Admin: token login (constant-time compare), signed HttpOnly/Secure/SameSite=Strict cookie for 30 days, rate-limited failed logins, every write requires a session. Multi-upload (phone picker and drag and drop) with per-photo progress, delete, drag reorder, optional caption, edit texts. Hebrew error messages.
- Accept JPEG, PNG, WebP up to 30 MB each, validated on the server.
- Images served through the Worker with long Cache-Control and ETag.

## Brand Commitments

- No existing name, logo or assets. Until the owner edits them, the site shows neutral Hebrew placeholders (confirmed by the user).
- Visual direction is pinned by the user (recorded in the surface brief), and must not copy the logo, name or assets of any existing brand.
- Public page content is exactly: title, subtitle, gallery, phone, WhatsApp. No extra sections (confirmed by the user).

## Evidence on Hand

No real photographs, reviews, address or prices exist in the repository. Do not invent reviews, ratings, amenities, prices or locations. Test images used during development are synthetic and are not committed as site content.

## Product Principles

1. Extreme operational simplicity: every routine action happens inside the site, from a phone.
2. The photographs are the product; the interface recedes.
3. The original file is sacred: stored untouched, never recompressed.
4. Nothing to maintain: no database, no build, no services beyond one Worker and one bucket.
5. Failure speaks Hebrew: every error tells the owner what happened and what to do.

## Accessibility & Inclusion

Hebrew RTL throughout. Large tap targets for the owner on a phone. Lightbox and reordering must be operable by keyboard as well as touch.
