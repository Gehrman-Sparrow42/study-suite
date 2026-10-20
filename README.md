# Study Suite V3

A reusable system for turning a whole course into **one editable HTML reading resource**. The final file contains its own CSS, JavaScript and chosen images. Python builds the document; Codex reads and interprets course materials. No backend, API key, account, database or framework is required to build or read it.

Open `output/Demo_Study_Suite.html` in a browser. This is a small synthetic demonstration, not a course summary. The original reference package is preserved separately.

Private source repository: [Gehrman-Sparrow42/study-suite](https://github.com/Gehrman-Sparrow42/study-suite).

## Read, edit, save

- Read top to bottom or jump using Contents. On phones, Contents opens a drawer.
- Learn shows the teaching explanations. Review hides explanatory bodies while retaining core statements, formulas, sequences, comparisons and takeaways. Search temporarily exposes matching explanations in either mode. Only matching sections appear in Contents while searching; section jumps retain the query. Clear the search to restore the full course. Unrelated source notes stay closed.
- Click headings, paragraphs, list items, captions or table cells to edit. An expanded explanation is one editing area: Enter adds paragraphs, and Backspace can join adjacent paragraphs. Added text stays editable after export/reopen. Rich text pasted from elsewhere becomes plain text. Use **Edit formula** (or **Edit** beside inline math) to change raw LaTeX, then Apply formula.
- Click a figure to enlarge it. Zoom in permits panning inside the figure window. Escape or Close figure dismisses it.
- **Save Progress** exports your current edition, including edits and embedded figures. Chromium browsers may offer a file picker; Firefox and other browsers use a download. A fallback download message says only that the download was requested: check Downloads before closing the tab.
- **Auto-save** connects your chosen HTML file in Edge/Chrome. Choose the HTML to overwrite once, then edits save after a 700 ms typing pause. You can choose a new edition instead. The first connection immediately saves the current page; later changes need no Save Progress click. Clicking Auto-save again turns it off. Reconnect after reopening the document; file permission is deliberately not embedded in exported HTML.
- Browser recovery stores the latest text/formula changes locally after a 300 ms pause, even without Auto-save. If you reload with unsaved changes, **Restore browser recovery** appears in Contents for a matching document baseline. Restore is explicit. Browser storage can be blocked, cleared or full; the sidebar reports recovery failure. This recovery is local to the browser/profile and file location and does not synchronize devices. Embedded figures remain in the HTML rather than the recovery record.
- Unsupported browsers such as Firefox use recovery and Save Progress downloads. Auto-save never simulates saving through repeated downloads. A denied automatic write pauses Auto-save, preserves edits/recovery and reports the failure. The sidebar distinguishes pending changes, browser recovery and confirmed HTML writes.
- Reopen the saved HTML to continue. Browser edits are embedded in a portable snapshot; the weekly updater can reconcile them into the next course JSON. An ordinary rebuild still starts from JSON, so keep personal editions separate and use the update workflow below.
- Cancelling a save keeps edits in the current tab. A close-tab warning protects unsaved changes where browsers permit it. After a fallback download the warning remains, because browser download completion cannot be confirmed by page JavaScript.

MathJax 3.2.2 is a pinned, optional CDN dependency. Without network access, raw editable LaTeX remains visible and the reader still works. All diagrams are embedded. System fonts require no downloads.

## Build the demo

Python **3.11 or newer**, standard library only. In PowerShell:

```powershell
Set-Location 'C:\Users\Berkay\Desktop\Ders\study-suite'
python scripts/build.py demo/sample_course.json --output output/Demo_Study_Suite.html
python scripts/validate.py output/Demo_Study_Suite.html
Start-Process output/Demo_Study_Suite.html
```

Paths also work from another directory if passed as absolute paths. With no `--output`, the output filename from config is written under this project's `output/` directory.

## Use it for a new course

Follow the [high-yield authoring checklist](guidelines/AUTHORING_CHECKLIST.md): concise English, useful bullets, compact domain-specific formula keys and a verified distinction between Learn and Review. The checklist also covers saved-edit preservation, source coverage and delivery checks for revisions.

Put all PDFs, PPTX files, notes and other source materials for **one course** in one input directory. This may be an existing course folder; there is no need to move it. Optional course settings go in a TOML file. Intermediate notes, the topic map, JSON and selected images can go in `work/<course>/` (ignored by Git).

Paste this instruction into Codex:

> Use the existing V3 Study Suite system at C:\Users\Berkay\Desktop\Ders\study-suite and all course materials in [COURSE FOLDER]. Read its AGENTS.md and content/visual guidelines. Produce one unified English study HTML using the existing template and deterministic builder. Default to balanced_high_yield: near-complete major-topic coverage, clear teaching explanations, source vocabulary, selective slide-first visuals, and worked examples where useful. No quizzes, flashcards, question banks or dedicated practice sections. Keep a source inventory, topic coverage map, uncertainties and progress checkpoints. Do not regenerate the reusable template. Validate the result and test edit/save/reopen. Report the output path and any important unreadable sources or omissions.

Optional natural-language additions: “I have two days; compress secondary detail,” “Keep obscure definitions because the instructor emphasizes them,” or “Use violet as this course's accent.” Codex translates these into content decisions and course config; **the deterministic builder does not interpret natural language or choose exam topics**.

Configuration precedence: current user instruction → explicit `--set` task override → course TOML → `config/defaults.toml`. For normal use, ask Codex to write overrides into the course TOML, then run:

```powershell
python scripts/build.py work/my-course/course.json --config work/my-course/course.toml --output output/My_Course.html
python scripts/validate.py output/My_Course.html
```

`--set` accepts a TOML assignment for scripted workflows. Example without shell quoting ambiguities: `--set include_review_mode=false`.

Depth, days remaining and visual density are **authoring guidance**, recorded in configuration; they do not mechanically delete paragraphs or generate images. The author applies them before building. Visual policy, web-image permission, accent, title, filename, source-label visibility and Review availability are applied by the builder. `theme_accent="auto"` uses the calm teal default; Codex may select a named accent from the subject. Semantic colors always stay fixed. `language="en"` is required; the author must inspect the prose for English because the builder checks language metadata, not language detection. `practice="off"` is the only accepted practice setting.

## Project map

| Path | Purpose |
| --- | --- |
| `PROGRESS.md` | Completion state, decisions, checks and exact resume steps |
| `AGENTS.md` | Rules for future Codex course tasks |
| `config/` | Documented defaults and optional course overrides |
| `guidelines/CONTENT_GUIDELINES.md` | Coverage, selection, source alignment, depth and uncertainty handling |
| `guidelines/VISUAL_GUIDELINES.md` | Semantic colors, component selection, asset pipeline and reading design |
| `guidelines/CONTENT_SCHEMA.md` | JSON fields, block types and examples |
| `template/` | Reusable HTML structure, CSS and reader JavaScript |
| `scripts/build.py` | Strict structured-content renderer and asset bundler |
| `scripts/validate.py` | Generated/exported HTML structural validator |
| `scripts/update.py` | Source scan, conflict-aware reconciliation and weekly additions |
| `scripts/course_state.py` | Stable course/block identities and portable edit snapshots |
| `guidelines/WEEKLY_UPDATES.md` | Incremental new-week workflow and migration limits |
| `demo/` | Synthetic authored content and original SVG diagram |
| `output/Demo_Study_Suite.html` | Ready-to-open, portable demonstration |
| `tests/` | Builder and real browser regression checks |

## Verification

```powershell
python -m unittest discover -s tests -p 'test_*.py' -v
node --check template/app.js
```

Browser testing is optional for people merely building a course, but expected when changing reader interactions. Tests use the Python Playwright package, installed Microsoft Edge, and Playwright Firefox:

```powershell
python -m pip install playwright
python -m playwright install firefox
python -X utf8 tests/browser_smoke.py
python -X utf8 tests/browser_updates.py
python -X utf8 tests/browser_autosave.py
```

The test saves screenshots, downloaded edited documents and `results.json` in ignored `tests/artifacts/`. It opens local files, edits text/formulas/table cells, downloads and reopens the actual result, checks repeated exports, tests mobile widths, and exercises offline math and save cancellation/failure. The OS picker itself is mocked; the download/reopen paths are real. `TEST_RESULTS.md` records the latest setup run.

The validator detects structural defects, missing anchors, duplicate IDs and non-embedded images. It is not an HTML standards conformance checker, a scientific auditor or proof that all source material was understood. Coverage and scientific accuracy require the authoring checks in the guidelines.

## Resuming or extending

New weeks can be appended without summarizing Weeks 1–5 again. Numbered weeks sort numerically in the reader and Contents. Provide the latest course JSON, latest saved personal HTML and new source files; Codex authors only the new material as a delta. The updater imports browser text/formula edits, rejects conflicting source edits and writes new JSON/HTML editions. See [the weekly guide](guidelines/WEEKLY_UPDATES.md) for the full process. Ready-to-open synthetic examples are `output/Weekly_Weeks_1_to_5.html` and `output/Weekly_Weeks_1_to_6.html`.

Read `PROGRESS.md` first. Reuse existing files and completed checks. New courses should ordinarily change only content, assets and course config. If interrupted, save authored sections and update the source inventory/coverage map so a later session can continue without repeating completed material. Never rebuild over an edited personal export.


### Expanded bullet explanations

Use `learn_only: true` on a block containing expanded teaching material, including bullet lists. It hides the whole block in Review and labels it Further explanation. Search can reveal matching explanations temporarily. Leave formulas, their symbol guides, essential assumptions, worked steps and short takeaways in persistent blocks. Bullet formatting by itself does not determine whether content belongs in Review. The default is false, preserving existing course behavior.

Run the focused regression with `python tests/browser_learn_review.py --browser edge` (or `firefox` / `all` with the corresponding Playwright browser installed).
