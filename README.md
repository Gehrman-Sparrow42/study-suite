# Study Suite

Turn course materials into **editable, portable HTML study readers** with Learn and Review modes, embedded figures, and saved notes. Open the finished file directly in a browser; no server or account is required.

The repository contains the reusable builder, reader, authoring guidelines, tests, and synthetic demos. An author or AI coding assistant interprets the supplied course materials and writes structured content. The Python builder renders that content; it does not summarize PDFs or decide what will be on an exam.

## Try it

[Download the repository ZIP](https://github.com/Gehrman-Sparrow42/study-suite/archive/refs/heads/main.zip), extract it, and open **`output/Demo_Study_Suite.html`** in your browser. No installation is needed to read or edit the demo.

The demo uses invented teaching material. Real lecture files, recordings, personal course notes, and generated course readers are not included.

## Build your first reader

Building requires **Python 3.11 or newer**. The builder uses only the standard library.

```sh
git clone https://github.com/Gehrman-Sparrow42/study-suite.git
cd study-suite
python -X utf8 scripts/build.py demo/sample_course.json --output output/Demo_Study_Suite.html
python -X utf8 scripts/validate.py output/Demo_Study_Suite.html
```

Open the generated HTML in Edge, Chrome, Firefox, or another modern browser. You can also download the ZIP instead of using Git. Run the commands from the extracted repository folder. If your system calls Python `python3`, use that command instead.

The HTML embeds its CSS, JavaScript, and selected figures. **MathJax 3.2.2 is an optional CDN dependency:** without internet access, formulas remain available as raw editable LaTeX. System fonts need no downloads.

## What the reader does

- **Learn and Review:** Learn includes the full authored explanation. Review hides expanded detail while retaining core statements, essential assumptions, formulas, process stages, comparisons, and worked steps.
- **Search and navigation:** Jump through Contents, fold topics or individual explanations, and search the course. Search temporarily reveals matching explanations and restores the previous state when cleared. Mobile Contents uses a drawer.
- **Clear visual structure:** True-black background, semantic heading colors, short labelled explanations, comparisons, process chains, and related figures. Responsive groups react to viewport changes, disclosure changes, and editing.
- **Editable content:** Click headings, prose, lists, captions, or table cells to edit. Formula controls edit raw LaTeX. Export preserves the supported structure; pasted rich text becomes plain text.
- **Embedded figures:** Open a figure to enlarge it, zoom, and pan. Figures travel with the saved file.
- **Portable progress:** Save your edited reader as HTML and reopen that file to continue. The weekly update workflow can reconcile its text and formula edits with newly authored material.

This is an explanation-based reading resource. It has no quiz, flashcard, self-test, or question-bank interface. Worked examples and explanations of supplied course questions are supported.

## Save your work

| Option | Behavior |
| --- | --- |
| **Save Progress** | Exports the current reader with edits and figures. Supported Chromium browsers may offer a file picker; other browsers download a file. Check that the download completed before closing. |
| **Auto-save** | In supported Edge/Chrome environments, choose an HTML file once. The current page saves immediately, then edits save after a 700 ms typing pause. Reconnect after reopening; file permissions are not embedded in the HTML. |
| **Browser recovery** | Stores recent text/formula edits locally after a 300 ms pause. A matching baseline offers an explicit restore action. Storage is specific to the browser/profile and file location; it can be blocked or cleared. |

A denied write pauses Auto-save and preserves edits/recovery. Unsupported browsers use manual exports and recovery. Cancelling a save leaves your edits in the current tab. A download request cannot prove that the browser finished writing the file.

**Keep your saved personal HTML separate from fresh builds.** An ordinary build starts from source JSON, so use the update workflow to bring personal edits into a later edition.

## Create a course with an AI assistant

Keep one course's PDFs, slides, notes, and other inputs together in an existing course folder. Put intermediate authored JSON, assets, source inventories, and coverage decisions under `work/<course>/`, which Git ignores.

Give your assistant the repository path and this brief:

> Use this Study Suite repository and the course materials in [COURSE FOLDER]. Read AGENTS.md and the content, visual, schema, and authoring guidelines. Normally produce two separately authored English editions: focused_learning for complete, manageable first reading, and balanced_high_yield as the detailed reference. Let depth follow course density and my requested exam scope, without word quotas. Preserve source terminology, important conditions, formulas, figures, and worked reasoning. Use short semantic explanations, comparisons, and process chains where they improve understanding. State each worked problem, givens, units, and required output before solving it; keep essential information visible in Review. Preserve existing editions and personal edits. Build and validate the readers, verify desktop/mobile layout and Learn/Review, and test actual edit/export/reopen. Deliver the HTML files and rebuildable source bundles, with source gaps stated clearly. Check factual accuracy against supplied sources yourself; do not launch a scientific-review subagent unless I explicitly request one.

Current instructions can change the normal two-edition workflow. For example, an elective can have one scoped reader: explain the teacher's material normally, focus peer presentations on their supplied questions and nearby reasoning, and mark missing question sets pending. Do not invent an expanded exam syllabus or assume embedded discussion prompts are official exam questions.

The two usual editions have separate content, stable course IDs, configuration, coverage maps, and dated filenames. Each has its own Learn/Review modes. The builder does not shorten a detailed edition automatically. Core/cram is optional.

See the [authoring checklist](guidelines/AUTHORING_CHECKLIST.md), [content guidelines](guidelines/CONTENT_GUIDELINES.md), [visual guidelines](guidelines/VISUAL_GUIDELINES.md), and [content schema](guidelines/CONTENT_SCHEMA.md).

## Configure and build a course

Use `config/course.example.toml` or `config/focused.example.toml` as a starting point. After authoring the JSON:

```sh
python -X utf8 scripts/build.py work/my-course/focused/course.json --config work/my-course/focused/course.toml --output output/My_Course_Focused.html
python -X utf8 scripts/validate.py output/My_Course_Focused.html
python -X utf8 scripts/build.py work/my-course/detailed/course.json --config work/my-course/detailed/course.toml --output output/My_Course_Detailed.html
python -X utf8 scripts/validate.py output/My_Course_Detailed.html
```

Settings resolve in this order: current authoring instruction → explicit `--set` override → course TOML → `config/defaults.toml`. An example CLI override is `--set include_review_mode=false`.

Depth, time remaining, and visual density guide the author; they do not mechanically summarize or remove content. Builder settings control options such as accent, title, output filename, image policy, source labels, and Review availability. English is required (`language="en"`); practice is disabled (`practice="off"`). See the config examples for supported fields.

## Add new weeks without losing notes

Use the latest course JSON, latest saved personal HTML, and new source files. Author new material as a delta while preserving existing course, section, and block IDs. `scripts/update.py` scans source changes, reconciles saved text/formula edits, and writes a new edition. Conflicting edits or revised processed sources require reconciliation.

Follow the [weekly update guide](guidelines/WEEKLY_UPDATES.md). Synthetic examples are included at `output/Weekly_Weeks_1_to_5.html` and `output/Weekly_Weeks_1_to_6.html`.

## Repository map

| Path | Purpose |
| --- | --- |
| `AGENTS.md` | Operating rules for AI-assisted authoring and maintenance |
| `guidelines/` | Content selection, visual design, JSON schema, authoring checks, and weekly updates |
| `config/` | Defaults and example course settings |
| `template/` | Reusable HTML, CSS, and reader JavaScript |
| `scripts/build.py` | Structured-content renderer and asset bundler |
| `scripts/validate.py` | Generated/exported HTML structural checks |
| `scripts/update.py` | Source scanning and conflict-aware weekly updates |
| `scripts/course_state.py` | Stable identities and portable edit snapshots |
| `demo/` and `output/` | Synthetic source material and ready-to-open demos |
| `tests/` | Builder, update, layout, and browser regression checks |
| `PROGRESS.md` and `TEST_RESULTS.md` | Development history, decisions, and recorded verification |

Private course inputs and outputs should stay outside tracked paths. `work/`, `input/`, and browser test artifacts are ignored. Before contributing, inspect your Git diff and avoid adding personal notes, credentials, copyrighted course materials, or generated real-course exports.

## Development and verification

Run the deterministic tests and JavaScript syntax check:

```sh
python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v
node --check template/app.js
```

Browser regression tests additionally require Playwright, installed Microsoft Edge for Edge checks, and Playwright Firefox for Firefox checks:

```sh
python -m pip install playwright
python -m playwright install firefox
python -X utf8 tests/browser_smoke.py
python -X utf8 tests/browser_updates.py
python -X utf8 tests/browser_autosave.py
python -X utf8 tests/browser_learn_review.py --browser edge
```

Tests retain evidence under ignored `tests/artifacts/`. Browser checks cover editing, actual export/download and reopen, mobile layouts, recovery, save failure, and offline math. OS picker behavior is mocked in automated tests. Refer to [TEST_RESULTS.md](TEST_RESULTS.md) for checks actually run and their environment limitations.

The structural validator catches issues such as missing anchors, duplicate IDs, and non-embedded images. Source coverage, factual accuracy, readable composition, and useful Learn/Review boundaries still need author checks. For reader changes, verify full widescreen viewports as well as mobile, including navigation open/closed and saved-file reopening.
