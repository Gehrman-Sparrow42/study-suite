# Visual and interaction guidelines

The workspace uses available width beside navigation and expands when navigation closes. Use intrinsic CSS grid reflow to place readable cards into as many columns as fit; collapse naturally to one column when space is limited. Keep prose measure bounded inside cards, rather than imposing a fixed pixel cap on the entire page or computing viewport-specific left offsets. Preserve DOM reading order. Figure width follows its card and caption measure. Inspect full-window 16:9 screenshots at the user's actual desktop proportions (2560x1440 here), with navigation open and closed, plus laptop and mobile sizes. A cropped card or near-square preview cannot establish wide-screen layout quality.

## Design direction

The user-selected Bionano L 1 to 10 reader is the primary experience reference. Future suites should be substantially closer to that reader than the earlier prose-heavy V3 pages. Use its compact topic grouping, distinct semantic titles, expandable depth, visual sequences and varied information structures. Preserve true black, direct editing, accessible navigation and reliable export. Refine implementation weaknesses such as fixed-height clipping while retaining the reference experience. Default text uses local Segoe UI/Arial; no external font dependency.

The canvas is #000000. Charcoal panels separate content without flooding an OLED display. Semantic colors never vary with course accent:

| Category | Meaning | Text accent |
| --- | --- | --- |
| definition | Vocabulary, definitions, structures | #93b9ec blue |
| process | Mechanisms, pathways, algorithms, sequences | #8bceb0 green |
| formula | Equations, hard rules, parameters | #e1bd7e amber |
| warning | Inhibitors, failure states, pitfalls | #e2a0a0 red |

A separate course accent affects heading metadata and navigation. Named themes: teal/auto, violet, blue, green; custom #RRGGBB accepted. Check contrast when using custom colors. Titles and written statements carry meaning in addition to color; avoid a redundant category label above each title.

## Choose components by teaching value

Optimize comprehension and scanning: a clear core statement, short explanatory
paragraphs, labelled parallel points, visible conditions, and a readable text
measure. Use existing processes for sequences and comparisons for real contrasts.
Choose structure for the information; do not add decoration, dashboard controls,
extra cards or emphasis merely to make a page look busy. Body and lead text have
a 75ch maximum measure; figures, formulas and tables retain their useful width.

- Related concepts share a responsive topic-local grid. Width determines column count, not a hardcoded screen coordinate. Keep a coherent row-major reading order; avoid dense multi-column layouts for long derivations.
- Use `presentation="flow"` for process blocks that represent a real chain. Present short named stages connected by arrows, with a visually distinct final stage. Use a normal numbered list for procedural analysis, branching steps or long worked calculations. Never draw arrows between merely related facts.
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

## Reference direction: Bionano viewing experience

The user selected the supplied Bionano L 1 to 10 reader as a broader experience reference, beyond a single spacing correction. Carry forward its clear section/topic hierarchy, semantic-colour concept titles, compact labelled facts, paired related explanations, wide comparison tables and distinct synthesis callouts. Use quiet secondary metadata and avoid a repeated category label above every heading. Keep the true-black palette and a restrained type scale. Make the layout adapt to available space with intrinsic grid sizing; use a single column when reading width demands it. Tables and synthesis may span their topic group; a figure should sit near its explanation. Do not copy the reference's fixed-height clipping, hover movement, inaccessible toggles, or unrelated content/features. Learn/Review controls overall depth; native explanation disclosures and accessible section folding let the reader control individual topics. All start expanded and use natural content height. Preserve readable prose, complete qualifications, keyboard access, editing and export.

Author concise topic-local groups: related definitions can be compared side by side; mechanisms should read in order; wide tables should compare consistent dimensions; a short takeaway should synthesize rather than repeat an entire section. The goal is an easy reading path, not a dashboard or maximum card count. Future courses should be authored for this structure rather than styling long transcripts as cards.

### Process flows and disclosure behavior

`process` blocks accept optional `presentation: "flow"` (or `"list"`, the default). Steps remain ordered, fully editable text with stable snapshot pointers. Short bold stage names aid scanning; preserve essential qualifications. The last stage is distinguished visually without fabricating an output or changing the science. Explanations use native details/summary, open in Learn and hidden in Review. Section buttons fold a topic group; navigation opens its destination, search reveals matches and restores prior fold/disclosure state when cleared. Export must not accidentally save a temporary search expansion. No fixed maximum content heights.
