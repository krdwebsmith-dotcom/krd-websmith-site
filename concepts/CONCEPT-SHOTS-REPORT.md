# Concept sites + screenshots — delivery report

Built: 2026-08-18. Only `krd/concepts/` and `krd/assets/shots/` were touched.

## Concept pages (self-contained single-file HTML, Google Fonts + hotlinked Unsplash photos)

| File | Bytes | Art direction |
| --- | --- | --- |
| `krd/concepts/apex/index.html` | see `ls` | Near-black charcoal, electric-orange accent, Saira Condensed uppercase display + Barlow body + IBM Plex Mono labels, notched buttons, 3-column package comparison table (stacked price cards under 760px), glossy car photography |
| `krd/concepts/noir/index.html` | " | Bone/off-white ground, espresso ink, brass accent, Cormorant Garamond display + Jost UI type, dotted-leader price list, dark editorial split panel, day picker + time-slot chips booking card |
| `krd/concepts/evercrest/index.html` | " | Deep forest green + warm stone, Bitter slab headings + Karla body, copper CTA, utility top bar, seasonal 6-card service grid, 4-step "Get an estimate" qualification form, service-area list |

Helper: `krd/concepts/_shoot.js` (Playwright capture script; serves from `python3 -m http.server 8777` inside `krd/concepts`).

## Screenshots — `krd/assets/shots/` (PNG, all ≤1440px wide, i.e. under the 1600px cap, no downscale needed)

| File | Dimensions | Bytes |
| --- | --- | --- |
| apex-desktop.png | 1440x900 | 589613 |
| apex-desktop-full.png | 1440x6274 | 2195835 |
| apex-mobile.png | 390x844 | 89552 |
| apex-mobile-full.png | 390x10232 | 889730 |
| apex-detail.png | 1176x626 | 47903 |
| noir-desktop.png | 1440x900 | 230912 |
| noir-desktop-full.png | 1440x6756 | 2675012 |
| noir-mobile.png | 390x844 | 95100 |
| noir-mobile-full.png | 390x10847 | 1177178 |
| noir-detail.png | 538x856 | 37396 |
| evercrest-desktop.png | 1440x900 | 1164239 |
| evercrest-desktop-full.png | 1440x8046 | 5211457 |
| evercrest-mobile.png | 390x844 | 315934 |
| evercrest-mobile-full.png | 390x13097 | 2581086 |
| evercrest-detail.png | 597x1161 | 64204 |

Detail shots: apex = package/pricing comparison table; noir = booking card with day picker + time-slot chips; evercrest = 4-step estimate form (step 1 active).

## QA performed

- Every capture waited on `networkidle`, `document.fonts.ready`, and all `HTMLImageElement.complete`; the script logs any image with `naturalWidth === 0` — final run logged none.
- Mobile (390x844, `isMobile: true`) `document.documentElement.scrollWidth === 390` on all three; the only elements extending past the viewport are inside the intentionally `overflow:hidden` Apex marquee strip.
- All screenshots visually reviewed: display fonts render (Saira Condensed / Cormorant Garamond / Bitter), no fallback flash, no clipped text, no grey image boxes.
- Element screenshots take a temporary `header{position:static}` style so the sticky header does not overlay the captured section.
- Photography was contact-sheeted and vetted before use so subjects match the copy (detailing/barbering/temperate Ontario-plausible landscaping — no palm trees, no bathrooms).
- Metadata stripped from every PNG (`mogrify -strip`).
