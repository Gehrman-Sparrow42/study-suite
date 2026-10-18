# Content schema · version 3

Use UTF-8 JSON. All text is English. Text fields are **plain text**, not Markdown or arbitrary HTML. The builder escapes markup. Within summaries, bodies, steps and table cells, explicit `\(LaTeX\)` denotes editable inline mathematics. In JSON, escape each backslash: `"The quantity is \\(q=12\\)."`. For display math, use a `formula` block with raw `latex` and no delimiters. Unicode symbols are also useful in prose.

## Course object

```json
{
  "schema_version": 3,
  "language": "en",
  "synthetic": false,
  "title": "Course title",
  "subtitle": "Brief scope and reading orientation.",
  "included_section_ids": ["foundations"],
  "sections": [
    {
      "id": "foundations",
      "title": "Foundations",
      "intro": "A short bridge into this section.",
      "blocks": [
        {
          "type": "concept",
          "category": "definition",
          "title": "The core idea",
          "summary": "The essential teaching statement remains visible in Review.",
          "body": "Explain how and why. Separate paragraphs with two newline characters.",
          "source": "Lecture 1, slides 4–6."
        }
      ]
    }
  ]
}
```

`schema_version`, `language`, `synthetic`, `title`, `subtitle`, `included_section_ids` and a nonempty `sections` array are required. `synthetic` must be explicitly false for real course output. The builder rejects obvious demo/placeholder markers in production data; the author still verifies the whole document.

Section IDs must be unique lowercase slugs matching `[a-z][a-z0-9-]*`. The generated anchor is `section-<id>`, preventing collisions with reader controls. `included_section_ids` must contain each section ID exactly once: reconcile it with the saved topic coverage map. Every section needs a nonempty `blocks` list. `intro` is optional.

## Common block fields

- `type`: one of the types below. Unknown types are rejected, including quizzes and flashcards.
- `title`: required, editable heading.
- `summary`: required for every type except figure; visible in both reading modes. Keep essential assumptions here or in persistent steps.
- `body`: optional expanded explanation. Two newlines separate paragraphs. Hidden in Review, temporarily visible when searching.
- `category`: `definition`, `process`, `formula`, or `warning`. Defaults to process for process blocks, formula for formula/worked blocks, definition otherwise.
- `source`: optional short provenance text, displayed in collapsed Source note details when source labels are enabled.
- `compact`: optional boolean; pairs short concept/prose blocks on wide screens. Other types remain full width.

## Block types

| Type | Extra fields | Behavior |
| --- | --- | --- |
| `concept` | none | Core concept or limitation; optional compact layout |
| `prose` | none | Explanatory connection; optional compact layout |
| `process` | `steps`: nonempty array of strings | Persistent numbered mechanism/sequence |
| `formula` | `latex`: raw LaTeX string | Rendered display formula, source editor, explanatory body |
| `comparison` | `headers`: strings; `rows`: arrays of strings | Table with matching row widths and editable cells |
| `worked` | `steps`: nonempty array of strings | Fully explained calculation or application; no answer interaction |
| `figure` | asset, origin, alt, caption, credit | Embedded image and zoomable lightbox |
| `review` | `steps`: nonempty array of strings | Section takeaway with persistent bullet points |
| `details` | optional body | Supplementary explanation, open in Learn by default |

Formula example:

```json
{"type":"formula", "title":"Average rate", "summary":"Change in amount per unit time.", "latex":"\\bar{r}=\\frac{\\Delta q}{\\Delta t}", "body":"Define the quantity and interval, and state the conditions."}
```

Figure example:

```json
{"type":"figure", "title":"Source diagram", "asset":"assets/lecture-1-slide-4.png", "origin":"slide", "alt":"Describe the important spatial or causal relationship.", "caption":"Explain what to notice.", "credit":"Lecture 1, slide 4; supplied course material."}
```

`asset` is relative to the JSON file's directory and must resolve inside that directory. Supported suffixes: png, jpg/jpeg, webp, svg. SVG must be static and self-contained (no scripts, external references, stylesheets, foreignObject, image or use elements); use simple shapes/text or rasterize complex artwork. Asset size limit: 8 MiB per image. Missing selected assets fail the build. A figure excluded by visual policy is not read.

`origin` is `slide`, `custom` or `web`. Web figures additionally require an HTTPS `source_url` and a `license` string. The author must verify rights; a metadata string does not establish permission. All assets are embedded locally; no hotlinks.

## Authoring constraints

The schema is deliberately narrow. It does not accept arbitrary executable HTML, custom widget code, question banks or review quizzes. For additional teaching patterns, first express the material through the existing components. Extend the reusable renderer only when the learning benefit justifies new maintenance and tests.

Browser edits modify the exported HTML, not this JSON. To incorporate those edits into a future rebuild, explicitly reconcile them into the authored source; never silently overwrite an edited edition.
