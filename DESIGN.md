---
name: Zimmer Gallery
description: A one-zimmer photo site presented like a fashion house's lookbook, with its back-room admin in the same black-and-white world.
colors:
  paper: "#ffffff"
  ink: "#000000"
  quiet: "#5e5e5e"
  hair: "#f1f1f1"
  line: "#d6d6d6"
typography:
  display:
    fontFamily: "Bellefair, Assistant, Times New Roman, serif"
    fontSize: "clamp(1.75rem, 1.15rem + 2.6vw, 3.25rem)"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "0.01em"
  headline:
    fontFamily: "Bellefair, Assistant, Times New Roman, serif"
    fontSize: "clamp(1.5rem, 1.2rem + 1.2vw, 2.25rem)"
    fontWeight: 400
    lineHeight: 1.2
    fontFeature: "lnum, tnum"
  title:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "22px"
    fontWeight: 600
    lineHeight: 1.3
    letterSpacing: "0.01em"
  title-section:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    letterSpacing: "0.04em"
  body:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.6
  body-admin:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.55
  small:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.6
    letterSpacing: "0.04em"
  small-open:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.7
    letterSpacing: "0.08em"
  label-action:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    letterSpacing: "0.1em"
  label-word:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 600
    letterSpacing: "0.14em"
  label-field:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 600
    letterSpacing: "0.06em"
  button:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 600
    letterSpacing: "0.1em"
  input:
    fontFamily: "Assistant, Arial Hebrew, Segoe UI, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
rounded:
  none: "0px"
spacing:
  gap: "6px"
  gap-wide: "8px"
  gutter: "20px"
  gutter-md: "40px"
  gutter-lg: "56px"
  tap: "48px"
  bar: "56px"
  block: "72px"
  section: "96px"
  section-wide: "140px"
components:
  action-bar-solid:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.label-action}"
    rounded: "{rounded.none}"
    height: "{spacing.bar}"
  action-bar-plain:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.label-action}"
    rounded: "{rounded.none}"
    height: "{spacing.bar}"
  word-control:
    textColor: "{colors.ink}"
    typography: "{typography.label-word}"
    padding: "0 12px"
    height: "{spacing.tap}"
  word-control-disabled:
    textColor: "{colors.quiet}"
  button-solid:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "0 22px"
    height: "{spacing.tap}"
  button-solid-hover:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
  button-outline:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.button}"
    rounded: "{rounded.none}"
    padding: "0 22px"
    height: "{spacing.tap}"
  button-outline-hover:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
  button-wide:
    width: "100%"
    height: "{spacing.bar}"
  button-disabled:
    backgroundColor: "{colors.hair}"
    textColor: "{colors.quiet}"
  input-field:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    typography: "{typography.input}"
    rounded: "{rounded.none}"
    padding: "10px 12px"
    height: "{spacing.tap}"
  photo-frame:
    backgroundColor: "{colors.hair}"
    rounded: "{rounded.none}"
  position-tag:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "1px 5px"
  delete-armed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.paper}"
    padding: "0 10px"
    height: "44px"
  viewer:
    backgroundColor: "{colors.paper}"
    textColor: "{colors.ink}"
    width: "100vw"
    height: "100dvh"
---

# Design System: Zimmer Gallery

## Overview

**Creative North Star: "The House Lookbook"**

The public page presents one zimmer the way a high-end fashion house presents a collection: the place is the garment and the photographs are the lookbook. White paper, black ink, and photographs at full width do all the work; the interface is a few small, exactly tracked words and a single name set in a fine high-contrast display face. Density is low and deliberate. Empty white is part of the composition, never filler to be designed away.

The admin is the back room of the same house. It uses the identical black-and-white material as a precise work surface: one column, 1px rules, square boxes, words as controls. It refuses the generic dashboard (sidebar, cards, coloured status badges, icon buttons), and it keeps the public page's discipline while trading the display face for plain Assistant weight.

Everything is Hebrew and right-to-left. Layout is written in logical properties, and numbers, phone numbers and file names sit in left-to-right islands inside the RTL flow.

**Key Characteristics:**
- Pure white ground, pure black ink, greys only as placeholder, secondary text, or divider; no accent colour anywhere.
- Photographs lead: the first photograph fills the phone's first viewport edge to edge.
- Small Assistant text (12 to 14px) with open tracking; Bellefair only for the name and the contact numbers.
- Controls are words: underlined, ruled beneath, or boxed in 1px black, never icons.
- Square edges, 1px rules, no shadows; depth comes from white covering white.
- One motion: photographs fade up from grey, and a tapped photo morphs into the white viewer.

## Colors

A strictly achromatic palette: black and white carry every role, and greys exist only to stand in for missing content or to step text back.

### Primary
- **Ink Black** (#000000): all text, every rule and box stroke, the solid WhatsApp half of the phone bar, solid admin buttons, the focus ring, the armed delete control, the position tag on admin thumbnails, and the selection fill. It is the only "accent" the system has.

### Neutral
- **Paper White** (#ffffff): the ground of every page, the full-screen viewer and its backdrop, the call half of the phone bar, field backgrounds, and inverted text on black. The browser theme colour is also white.
- **Quiet Grey** (#5e5e5e): secondary text only (captions, contact labels, counts, hints, disabled viewer controls, status lines). 6.4:1 on white, so it stays readable at 12px.
- **Hairline Grey** (#f1f1f1): the placeholder behind every photograph before it loads (public frames, admin thumbnails), the empty track of an upload progress bar, and the fill of a disabled admin button.
- **Divider Grey** (#d6d6d6): admin only. The quiet hairline between repeated rows (photo list, upload queue, setup steps), the resting border of caption fields, the disabled button stroke, and the desktop drop-zone frame. Structure that is not repetition uses Ink Black instead.

### Named Rules
**The No-Accent Rule.** Nothing is coloured. WhatsApp is black, not green; success and error are words, not hues. If a new element seems to need a colour, it needs a word or a rule instead.

**The Grey Is Absence Rule.** Hairline Grey means "a photograph will be here" or "unavailable"; Quiet Grey means "secondary". Neither is ever used as a surface tint, a card fill, or decoration.

## Typography

**Display Font:** Bellefair (with Assistant, then Times New Roman)
**Body Font:** Assistant, variable weight 200 to 800 (with Arial Hebrew, Segoe UI, Arial)

Both faces are self-hosted as WOFF2 with separate Hebrew and Latin subsets split by `unicode-range`, `font-display: swap`, and the Hebrew files preloaded.

**Character:** A single fine, high-contrast serif moment (the name) above a field of small, exact, openly tracked sans text. The contrast between one large refined line and everything else being small is the typographic identity.

### Hierarchy
- **Display** (Bellefair 400, clamp(1.75rem, 1.15rem + 2.6vw, 3.25rem), 1.1): the zimmer's name, centred in the masthead; also the 404 heading. Balanced wrapping, breaks anywhere for long names.
- **Headline** (Bellefair 400, clamp(1.5rem, 1.2rem + 1.2vw, 2.25rem), 1.2, lining tabular numerals): the phone and WhatsApp numbers in the contact footer, set left-to-right.
- **Title** (Assistant 600, 22px, 1.3): admin view headings (login, setup).
- **Title Section** (Assistant 600, 18px, 0.04em): admin block headings ("תמונות", "פרטי הצימר") over a black rule.
- **Body** (Assistant 400, 14px, 1.6): public page base. **Body Admin** (Assistant 400, 15px, 1.55): admin base, prose capped at 60ch.
- **Small** (Assistant 400, 12px, 1.6, 0.04em): captions under photos and in the viewer, in Quiet Grey. **Small Open** (12px, 1.7, 0.08em): the subtitle, max 34ch, in Ink.
- **Label Action** (Assistant 600, 13px, 0.1em): the two halves of the phone bar.
- **Label Word** (Assistant 600, 12px, 0.12 to 0.14em): word controls on the public page: desktop header contact links, viewer close/previous/next, the viewer counter.
- **Label Field** (Assistant 600, 13px, 0.06em): admin form labels; the optional marker beside a label drops to 400 Quiet Grey.
- **Button** (Assistant 600, 14px, 0.1em): admin boxed buttons.
- **Input** (Assistant 400, 16px): every admin field; 16px stops iOS zooming on focus.

### Named Rules
**The One Display Moment Rule.** Bellefair sets the name and the contact numbers on the public page and nothing else. It never sets a control, a caption, or anything in the admin, which does not load it.

**The Small and Open Rule.** Interface text stays at 12 to 15px with positive tracking (0.04 to 0.14em); emphasis comes from weight 600 and tracking, never from size jumps. There is no text between the 15px body and the 22px admin title.

## Layout

Mobile first, single column, with two breakpoints (720px and 1280px). Spacing is set in px on a loose, generous rhythm rather than a strict scale.

- **Gutters:** 20px on phones, 40px from 720px, 56px from 1280px, extended by safe-area insets.
- **Gallery grid:** one column with a 6px gap on phones; two columns with an 8px gap from 720px; six tracks from 1280px where each photo spans two (three across). Grid tiles are 4:5 portraits.
- **The lead photograph** spans every column. On phones it fills the first viewport exactly, from below the measured masthead down to the phone bar (minimum 320px). From 720px it shows at natural proportion, capped at 86vh.
- **Closed rows:** the last row is never ragged. A lone final photo becomes a full-width 16:9 plate; at three across, a trailing pair becomes two 3:2 half-width plates.
- **Caption slot:** from 720px every tile keeps the same caption slot height, so rows align whether or not photos have captions; a gallery with no captions drops the slot.
- **Masthead:** centred, 44px top / 36px bottom on phones, 72px / 56px from 720px. Contact words move into the masthead's inline-end edge from 720px.
- **Contact footer:** large white margins (96px top / 112px bottom on phones; 140px / 160px from 720px), entries stacked on phones and side by side with a 96px gap wider.
- **Phone bar:** fixed to the bottom on phones only, 56px tall plus safe area; the page reserves its height and scroll padding so nothing hides behind it.
- **Admin:** one centred column, max 760px, 40px top padding (56px from 720px) and 80px bottom; blocks separated by 72px. Photo rows are a grid of grip (44px), thumbnail (72px, 96px from 720px) and caption, with move/delete words beneath on phones and at the row end from 720px.
- **Tap targets:** 48px minimum for every control (44px for in-row word controls on phones).

### Named Rules
**The Photograph Leads Rule.** On a phone, the guest sees the place before reading anything beyond the name: the lead photograph meets the masthead and the phone bar with no gap.

**The Closed Row Rule.** A grid of photographs always ends square. Add a plate rather than leave a hole.

## Elevation & Depth

Completely flat. There are no shadows anywhere, on either surface, at rest or in any state. Depth is shown three ways only: the full-screen viewer is white over a white backdrop, so it replaces the page rather than floating on it; the fixed phone bar is separated by a single 1px black top rule; and a photo row being dragged in the admin lifts as a 1px black outline while the other rows slide aside. Hover on a photograph dims it to 86% opacity instead of raising it.

### Named Rules
**The Flat Paper Rule.** No `box-shadow`, no blur, no glow, no translucent overlay. If something must sit above something else, it covers it in white or gets a 1px black line.

## Shapes

Every corner is square (0px radius, declared explicitly on buttons and fields to defeat platform defaults). Lines are 1px: Ink Black for structure (the admin top bar's bottom rule, block heads, boxed buttons and fields, the phone bar's top rule, the empty-gallery frame, the error mark at the start of an error line), Divider Grey for repeated admin rows. A field marked invalid takes a 2px black outline, the only heavier stroke. Underlines are 1px with a 0.3em offset. The single drawn mark is the admin's drag grip: two horizontal 1.5px strokes, 18px wide and 7px apart. The favicon follows the same geometry: a black square holding a thin white square outline.

### Named Rules
**The Square Edge Rule.** Radius is 0 everywhere. No pills, no rounded thumbnails, no soft fields.

**The Hairline Rule.** Lines are 1px and black unless they divide repeated admin rows. A rule separates; it never decorates.

## Components

### Phone Bar (signature, public)
The two ways to reach the owner, one thumb away.
- **Shape:** fixed, full width, square, 56px tall plus the bottom safe area, 1px black rule on top.
- **Halves:** WhatsApp is solid (Ink ground, Paper text) and comes first; call is plain (Paper ground, Ink text). Both are words in Label Action.
- **Focus:** a 1px ring inset 4px, in the half's own text colour.
- **Visibility:** phones only (below 720px); wider screens get the same two words in the masthead.

### Word Controls (public)
- **Style:** a tracked 600-weight word, no box. Desktop header contact links and contact footer ways carry a 1px rule beneath (transparent at rest in the header, black on hover). Viewer buttons underline on hover.
- **Disabled:** Quiet Grey, no underline.
- **Contact numbers:** Bellefair numerals that gain a 1px black rule beneath on hover.

### Buttons (admin)
- **Shape:** square (0px), 48px minimum height, 0 22px padding, 1px Ink stroke.
- **Solid:** Ink ground, Paper text. The primary action on each view ("הוספת תמונות", "כניסה", "שמירת הפרטים").
- **Outline:** Paper ground, Ink text, for secondary actions (recheck, retry, dismiss).
- **Hover:** a full inversion, solid to outline and outline to solid. No transition.
- **Wide:** full width, 56px tall; the add-photos button on phones (auto width, minimum 280px, on desktop).
- **Disabled:** Hairline Grey ground, Quiet Grey text, Divider Grey stroke.

### Text Links (admin)
- **Style:** 13px words, 0.04 to 0.06em tracking, 1px underline at 0.3em offset, 44 to 48px tall: top-bar links, move up / move down, delete. Hover thickens the underline to 2px.
- **Armed delete:** the first tap turns "מחיקה" into a solid Ink block with Paper text in weight 600; the second tap confirms.

### Inputs / Fields
- **Style:** Paper ground, 1px Ink stroke, square, 10px 12px padding, 48px tall, 16px text. Phone fields and the token field are left-to-right.
- **Caption field:** in a photo row, 44px tall with a Divider Grey stroke that turns Ink on hover and focus.
- **Focus:** a 1px Ink outline flush with the stroke (0 offset).
- **Error:** a 2px Ink outline, plus an error line beneath.

### Error and Status Lines
- **Error:** 14px weight 600 Ink text with a 1px Ink rule on its inline-start edge, always prefixed by the word "שגיאה:". Never red.
- **Status:** 13px Quiet Grey, reserved height so layout does not jump; confirmations are brief words ("נשמר", "הסדר נשמר") that clear themselves.
- **Upload row:** file name (left-to-right) and state text over a 2px progress line, Ink filling from the right across a Hairline Grey track. A failed row hides the line, sets its state in Ink weight 600, and offers outline buttons.

### Photo Frame (public)
- **Style:** square-cornered, Hairline Grey ground showing the photo's true proportions before load (width and height attributes), cursor zoom-in.
- **Load:** the image fades from 0 to full opacity over the grey.
- **Caption:** Small text in Quiet Grey beneath, aligned to the inline start.

### Viewer (signature, public)
- **Style:** a full-screen `dialog`, white on a white backdrop, top row of counter and close, image contained in the middle, caption beneath (max 60ch), previous / next words at the bottom.
- **Counter:** a quiet "3 / 24" in Label Word with tabular figures, left-to-right.
- **Behaviour:** the tapped photo morphs into place via View Transitions where supported; swipe and arrow keys move between photos; buttons disable at the ends.

### Photo Row (signature, admin)
- **Style:** grip, square thumbnail on Hairline Grey with a small Ink position tag (Paper numeral, tabular) at its inline-start corner, caption field, move and delete words. Rows divided by Divider Grey lines.
- **Drag:** press the grip; the row lifts as a 1px Ink outline and the others slide aside; order saves itself and the count briefly reads "הסדר נשמר". Arrow keys on the grip and move up / down words give the same result without dragging.
- **Drop zone:** while files are dragged over it, the zone is covered in Paper with a double frame (1px Ink stroke and a 1px Ink outline inset 6px) and the words "שחררו כאן כדי להעלות". On desktop it rests inside a 1px Divider Grey frame.

### Navigation
- **Public:** no navigation bar. Only a skip link (Ink block, Paper text, 12px, appears on focus) and the contact words.
- **Admin top bar:** 56px, site name in 13px weight 600 on the inline start (truncates), two underlined text links ("צפייה באתר", "יציאה") on the inline end, a 1px Ink rule beneath.

### Motion
All motion uses one exponential ease-out (`cubic-bezier(0.16, 1, 0.3, 1)`) except the upload progress, which is linear. Photographs fade up over 400ms; the viewer morph runs 420ms with a 260ms page crossfade; hover dims a photograph over 200ms; admin rows slide aside over 220ms while sorting. Under `prefers-reduced-motion: reduce`, the fade, the morph and the row slide are all removed.

## Do's and Don'ts

### Do:
- **Do** let the first photograph meet the masthead and the phone bar edge to edge on phones.
- **Do** set every control as a word: tracked, weight 600, underlined, ruled beneath, or boxed in 1px Ink.
- **Do** keep every corner at 0px and every line at 1px.
- **Do** show state with words and weight: "שגיאה:" with a black inline-start rule for errors, a brief Quiet Grey word for saves.
- **Do** invert (Ink to Paper) for hover on boxed admin buttons, and add or thicken a 1px rule for hover on word controls.
- **Do** write layout in logical properties (inline-start, inline-end) and wrap numbers, phone numbers and file names in left-to-right islands.
- **Do** reserve a photograph's proportions with Hairline Grey before it loads, and fade it in over 400ms.
- **Do** keep tap targets at 48px (44px for in-row words on phones) and fields at 16px text.

### Don't:
- **Don't** introduce any colour beyond Ink, Paper and the three greys; not for WhatsApp, success, error or links.
- **Don't** use shadows, blur, glows, gradients or translucent overlays.
- **Don't** round any corner.
- **Don't** use icons, pictograms or icon fonts. The admin's two-line drag grip is the one drawn mark, and it stays a drawn pair of strokes.
- **Don't** set Bellefair on anything but the name and the contact numbers, and never in the admin.
- **Don't** wrap content in cards, panels or coloured badges; separate with 1px rules and white space.
- **Don't** animate anything beyond the photograph fade, the viewer morph, the row slide and the progress line.
