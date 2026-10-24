# Visual and interaction guidelines

## Design direction

The reference suites establish true black, semantic color, top-to-bottom reading, direct editing, navigation and clean export. V3 keeps these habits while replacing heavy glows, oversized fixed card grids, collapsed mobile sidebars and brittle fixed-height accordions. Use a restrained editorial hierarchy: compact course heading, numbered sections, readable prose, full-width mechanisms/derivations, optional paired short concepts. Default text uses local Segoe UI/Arial; no external font dependency.

The canvas is #000000. Charcoal panels separate content without flooding an OLED display. Semantic colors never vary with course accent:

| Category | Meaning | Text accent |
| --- | --- | --- |
| definition | Vocabulary, definitions, structures | #93b9ec blue |
| process | Mechanisms, pathways, algorithms, sequences | #8bceb0 green |
| formula | Equations, hard rules, parameters | #e1bd7e amber |
| warning | Inhibitors, failure states, pitfalls | #e2a0a0 red |

A separate course accent affects heading metadata and navigation. Named themes: teal/auto, violet, blue, green; custom #RRGGBB accepted. Check contrast when using custom colors. Labels carry meaning in addition to color.

## Choose components by teaching value

Optimize comprehension and scanning: a clear core statement, short explanatory
paragraphs, labelled parallel points, visible conditions, and a readable text
measure. Use existing processes for sequences and comparisons for real contrasts.
Choose structure for the information; do not add decoration, dashboard controls,
extra cards or emphasis merely to make a page look busy. Body and lead text have
a 75ch maximum measure; figures, formulas and tables retain their useful width.

- Short definitions can pair using `compact=true`; do not pair long mechanisms.
- Processes and worked calculations use a full-width numbered sequence.
- Formula blocks show a core statement, editable LaTeX and variable/assumption explanation. Inline math is supported using explicit `\(...\)` tokens in text.
- Comparisons use a table with horizontal scrolling at narrow widths.
- Prose supplies conceptual connections without extra visual ornament.
- Details are open by default in Learn; reserve them for supplementary expansion.
- Reviews give a short takeaway at natural boundaries. They do not ask the reader to answer questions.
- Figures have informative captions, alt text and a tap-to-enlarge modal with zoom/pan.
- Keep supporting figures compact and left-aligned rather than filling a wide empty panel. Put a useful diagram before the comparison it explains; group related information in reading order without duplicate captions. A methods table should compare methods, while hazards belong in a short associated list rather than an unrelated extra column.
- Deliver actual rendered screenshots after presentation changes so the user can assess the result immediately. Update these guides with reusable presentation improvements. Visual inspection complements behavior checks; an image alone does not verify editing or saving.

Do not add decorative charts, stock photography, giant hero banners, unrelated animation, card quotas or dashboard widgets. Keep headings and controls familiar. Test dense and short sections at desktop and phone widths.

## Selective visual pipeline

1. Prefer a useful professor-provided image/diagram/plot. Extract from PDF or PPTX with the tools available for that task. Save selected assets beside the course JSON, for example `assets/slide-12-diagram.png`. Record filename, page/slide, crop and any ambiguity in the source inventory.
2. Preserve axes, legends, scale bars, units and relevant labels. Inspect the crop at display size; do not use illegible extraction just because it exists. Crop/compress responsibly before embedding. Raster PNG/WebP/JPEG and simple static SVG are accepted.
3. If a simple relationship is clearer as a small original SVG, create one with readable text and a concise caption. Do not invent measured data. The builder rejects active SVG features and external references; use basic shapes, paths and text.
4. Web imagery is optional and last. Only if enabled and useful, obtain a permitted local copy from an educational/authoritative source. Record `source_url`, `license`, `credit` and `origin="web"`. Do not hotlink, scrape around access controls or block completion searching for the perfect picture.
5. Set `origin` to `slide`, `custom` or `web`. The builder embeds the selected local asset as a data URI. It rejects paths outside the content directory and files over 8 MiB; this is a per-asset guard, not an instruction to fill that budget. Keep actual assets much smaller where legibility allows.

`visuals=off` omits figure blocks; `slide_only` includes only slide-origin figures; `smart` allows all selected permitted figures. `allow_web_visuals=false` suppresses web-origin figures. `visual_density` guides selection rather than forcing an image count. Every concept must remain understandable in its written explanation when a visual is omitted.

## Editing and export invariants

Text stays in editable DOM nodes. Formula raw source stays in `data-raw`; MathJax output is replaceable. Exports restore raw math, remove only MathJax-generated resources, preserve educational images, reset transient search/modal state, and keep the selected reading mode. Never remove all SVG tags. Do not export the live DOM without cleanup.

Use block-safe containers for editable prose. Multi-paragraph explanations share one editing host; do not make each paragraph an isolated host or put block elements inside an editable p. Browser checks must type Enter/Backspace and confirm inserted text is still editable after export/reopen. Delegate formula/figure button clicks so reconstructed editing nodes remain interactive. Search opens details only to expose their own matches and restores prior detail state; section navigation retains the active query.

Save success is reported only after the picker write closes. Anchor downloads receive an honest “download requested” message. Test cancellation, denied writes, Firefox fallback, repeated export size, and reopening with/without MathJax access. Math rendering follows the [MathJax 3.2 dynamic typesetting and cleanup API](https://docs.mathjax.org/en/v3.2/web/typeset.html).
