# Adding another week

The normal new-course delivery has focused_learning and balanced_high_yield
editions. Apply the workflow below to each edition independently: author an
appropriate delta, reconcile that edition's latest saved HTML, retain its stable
course ID and save new dated outputs. Reuse the common input inventory and checked
facts, but keep each edition's coverage decisions and personal edits distinct.
Do not merge edits across editions or recreate the focused version by changing a
depth label. Explicit user requests can limit an update to one edition.

Keep one course JSON, its selected assets, a source registry and your latest saved HTML. The JSON is the authored version; the HTML snapshot records personal text and formula edits. Codex reads the new source and writes a delta. The updater reuses the earlier sections and rebuilds one portable reading document with all weeks.

## Normal workflow

1. Save your personal HTML, through Auto-save or Save Progress. A browser recovery copy alone is not an updater input: restore and save it first.
2. Put the new PDF/PPTX/DOCX/TXT/MD into the course's material directory. Keep authored notes, progress logs and generated files elsewhere so they are not mistaken for new sources.
3. Scan the sources against the latest course JSON:

   ```powershell
   python scripts/update.py scan work/my-course/course-r05.json --input 'C:/path/to/course-materials'
   ```

4. Give Codex this instruction:

   > Add the new Week 6 sources to this existing Study Suite. Read its AGENTS.md and guidelines/WEEKLY_UPDATES.md. Use [LATEST COURSE JSON], [LATEST SAVED PERSONAL HTML] and [MATERIAL DIRECTORY]. Scan first. Read only new sources plus earlier context needed for links; retain earlier teaching sections and personal edits. Author a delta with stable IDs, source hashes and source-to-week links. Keep worked examples, Learn/Review and no quiz/practice system. Reconcile browser edits with the updater, stop for conflicting changes, write new edition filenames, validate and browser-test the result. Update the course progress/coverage map.

5. Keep the delta beside the course JSON and existing assets. Apply it to fresh output filenames:

   ```powershell
   python scripts/update.py apply work/my-course/course-r05.json work/my-course/week-06.delta.json --input 'C:/path/to/course-materials' --edited-html 'C:/path/to/My_Course_personal.html' --output-course work/my-course/course-r06.json --output-html output/My_Course_r06.html
   python scripts/validate.py output/My_Course_r06.html
   ```

6. Open the new edition and check your notes and new week. The next update uses `course-r06.json` and the newest saved r06 HTML. Earlier editions are retained. Reconnect Auto-save to the intended new HTML file.

The updater does not summarize PDFs or call a model. It verifies identities/hashes, imports edits and appends already authored content. Numeric week labels sort 1, 2, 6, 10; sections within a week retain author order. Unnumbered legacy sections appear first. Multiple sections may share a week.

## Identity and preservation rules

- Assign an explicit stable `course_id`, stable section IDs and block IDs before starting incremental authoring. Never rename IDs just to change a heading. Older JSON without IDs still builds, but generated positional block IDs must be materialized and retained before reordering blocks.
- Course `sources` records each processed relative path, SHA-256 and positive integer week. Each added section has `week` and `source_files` pointing to the new sources assigned to that week. A source must be referenced; duplicate file content is rejected, even under a new name. New unprocessed duplicates are caught when applying the delta.
- If a previously processed file changes, append stops. Deliberately reconcile the revised material and its affected sections, update the registry and coverage map, then start a new addition. Missing old PDFs are reported but do not erase previously authored content. Keep selected image assets because rebuilding still embeds them.
- Browser edits merge by stable section/block identity. If JSON still equals the HTML's baseline, the browser change wins. An identical authored change is accepted. Conflicting changes to the same field, deleted targets, unrelated course snapshots or incomplete edit capture stop the update before publication.
- The snapshot preserves prose, paragraph breaks, headings, cells, steps, captions and raw inline/display formulas. Arbitrary rich formatting or new block structures are outside the plain-text authoring schema. Table rows/steps are indexed inside their stable block: adding/reordering them while reconciling browser edits may need manual reconciliation. Snapshot errors are reported rather than silently dropping notes.
- Legacy HTML from before snapshots needs one explicit manual reconciliation into JSON. Existing HTML does not automatically gain the new runtime; rebuild an edition after reconciling its notes. Never overwrite the only copy of an old personal edition.
- Updates refuse existing output filenames. Complete files are published exclusively. JSON and HTML are separate outputs: if a filesystem error prevents the second publication, retain the completed JSON checkpoint and choose a new HTML output after resolving the error. The old inputs are untouched.

## Synthetic demonstration

`demo/weekly_course.json` records Weeks 1–5; `demo/weekly_sources` also contains one new Week 6 text source. `demo/week_06.delta.json` contains the corresponding teaching material. No real course has been summarized.

```powershell
python scripts/update.py scan demo/weekly_course.json --input demo/weekly_sources
python scripts/update.py apply demo/weekly_course.json demo/week_06.delta.json --input demo/weekly_sources --output-course demo/weekly-r06.json --output-html output/My_Weekly_r06.html
```

The generated filenames above must not exist. This example intentionally omits `--edited-html`; supply your saved Weeks 1–5 HTML to import personal notes. The delivered clean Weeks 1–6 demo contains synthetic teaching material only. Browser tests additionally import six actual edited fields, add Week 6, make another note and append Week 7.
