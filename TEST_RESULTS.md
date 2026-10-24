# Setup verification · 2026-10-18

## Executed checks

- Python 3.13.15: 28 deterministic tests passed (12 builder and 16 weekly-update tests), including paragraph-nesting rejection and omitted optional introductions.
- Node JavaScript syntax check: passed.
- Generated HTML structural validator: passed.
- Microsoft Edge 155 (installed Chromium browser): full browser regression passed.
- Playwright Firefox 153: full browser regression passed.
- Actual local-file HTML download, reopen and second download passed in both browsers.
- The demo includes the weekly snapshot and Auto-save runtime. Repeated edited export sizes remain equal in each tested browser; see ignored tests/artifacts/results.json for current measurements.
- All three delivered demos pass structural validation: the general demo, Weeks 1–5 and Weeks 1–6.
- Edge/Firefox weekly-update browser tests pass: six actual edited fields survive the Week 6 addition, then another edit survives the Week 7 addition.
- Edge/Firefox autosave/recovery tests pass. The picker is mocked in both browsers to exercise identical queue behavior; this does not claim native Firefox file-write support. Writes go to a real backing HTML and its content is checked.

## Browser behavior covered

- True-black background; desktop navigation and scrollspy; short last-section activation at the bottom.
- Learn/Review preserves content and hides only expanded explanations.
- Search across core text, section introduction, raw formulas and hidden/closed explanations; no-result feedback and restored detail state.
- Main title, section heading/navigation label, paragraph and table-cell editing.
- Real Enter/Backspace editing across body paragraphs and in core statements; actual download/reopen verifies the inserted text is still editable, then types more notes and exports again.
- Search opens only matching details, restores prior state as the query changes, retains queries on section jumps, and restores all section links in exports. Search also works with an absent optional introduction.
- Inline-formula deletion/Undo and deliberate DOM reconstruction; delegated formula and figure controls still open the correct dialogs.
- Display and inline LaTeX editing, actual MathJax rendering, and raw-source preservation after export/reopen.
- Embedded SVG image loads after reopening; lightbox zoom and Escape/Close behavior.
- Export resets search filters and dialogs, preserves chosen reading mode and all edited content, and strips MathJax artifacts without deleting the figure.
- Mobile drawer opens/closes, navigation reaches the selected section, table scrolls within its container, no page-wide overflow at 390 px and 320 px.
- Offline/CDN-blocked math shows raw source while editing and saving remain usable.
- Picker cancellation produces no success claim; successful write confirmation follows write/close; denied write falls back to a real download.
- No uncaught page JavaScript errors in the two main browser suites.

## Weekly update coverage

- Source hashing, new/changed/missing reports, renamed identical content and duplicate additions.
- Numeric week sorting and stable section/block identity across reordered sections.
- Browser/source three-way merge, same-change acceptance, conflict rejection, wrong-course/unrecognized-field rejection and untouched old inputs.
- Exclusive output publication, existing output refusal, asset validation before publication, source hashes and week/source linkage checks.
- Legacy HTML/incomplete snapshot refusal, script-ending escaping and a repeated Week 7 addition.
- Real browser Enter-edited paragraphs, heading, raw formula, table cell, figure caption and calculation step are saved to a real download, reconciled and reopened in Edge/Firefox. Search and mobile navigation reach new content; embedded figures remain intact.

## Auto-save and recovery coverage

- Initial connection, immediate first write, subsequent debounced edits and one picker call per connection.
- A deliberately held write followed by newer typing: serialized writes never overlap, and the final backing HTML contains the newest version.
- Denied writes pause Auto-save; reload reveals explicit browser recovery and restores the latest unsaved heading.
- Recovery restores paragraphs, raw inline math and a working formula editor. An undo back to baseline is recoverable even when it produces no remaining changed fields.
- Actual Enter/Shift+Enter edits in core statements retain paragraphs and hard line breaks after recovery. A deliberately delayed failed manual write followed by newer typing produces a real fallback download containing that newest edit.
- Picker cancellation keeps Auto-save off. Unsupported API reports recovery/manual export. Simulated storage quota failure reports recovery unavailable while text remains editable.
- Explicit Save Progress while Auto-save is connected confirms the write. A successful manual write with newer concurrent typing reports that newer edits still need saving; fallback downloads report a request rather than disk completion.
- Exported/reopened documents reset file connection state. File handles are not serialized. Mobile 390/320 px toolbar fits, with Auto-save and Save visible; the 390 px screenshot was inspected.
- OS-native selection/permission behavior remains outside executed automation. Existing real downloads/reopen tests and mocked picker ordering/error tests complement the real backing-file autosave writes.

## Visual inspection and fixes

Inspected desktop overview, dense mechanism/formula section, phone overview, dense phone section and phone formula screenshots. Kept wide mechanisms and derivations, narrow-screen stacking, contained table/math overflow, and restrained typography. Changed the toolbar from translucent to opaque after seeing text behind controls; made status feedback temporary so it does not permanently cover reading material.

Export testing found and fixed empty runtime style attributes and duplicate MathJax context-menu styles across saves. Added cleanup for dynamically loaded MathJax extension scripts. Improved source-heading synchronization after paste and search matching for section introductions. Added bottom-of-page scrollspy handling.

The Argon review follow-up reproduced an Edge editing defect missed by text-replacement tests: Enter could create a div inside an editable p, and reopening moved the inserted content outside its editing host. Text remains in a legal block-level host now; body paragraphs share a single editor. Expanded tests pass in Edge and Firefox. The structural validator now rejects the affected p/block nesting. Source-note search clutter and query-clearing navigation were also corrected. Optional print styling and initial math-performance work remain deferred.

The original Flash High follow-up review ended at the official CLI's 300-second print timeout while its turn was still in progress. The old runner hid this behind a generic missing-output error. After diagnosing it, a focused recheck with an explicit 600-second budget completed in 389 seconds: structured output received, finish gate verified, no findings in the supplied editing/search corrections. The full report and metadata are retained in ignored work/followup-review/FLASH_REVIEW.md and FLASH_RESULT.json. This static review supplements the executed browser regressions; it does not independently run them or cover the entire system.

Flash High supplied a focused test checklist; Codex reviewed it, implemented tests, executed them locally and fixed confirmed issues. This was test-design assistance, not a claim that Flash executed tests. Local brief/result copies are under ignored work/.

Flash High also reviewed the autosave runtime (structured result, gate verified). Codex confirmed visual paragraph/hard-break loss during recovery and a stale snapshot in delayed manual-save fallback; both were corrected and covered by executed Edge/Firefox tests. Manual write failure now flushes recovery immediately, and write completion no longer restarts the newer edit's debounce. The claimed critical RFC-pointer crash was rejected: the builder intentionally generates bare schema paths, not RFC 6901 pointers. The report overstated permanent text loss/severity: raw newline text was retained, but visual formatting needed reconstruction. Existing edit timers and beforeunload recovery also made its manual-failure loss scenario less general than claimed. Full report/metadata: ignored work/autosave-review/FLASH_REVIEW.md and FLASH_RESULT.json.

A focused Flash High recheck also returned structured output with gate verified. Codex confirmed and corrected status clarity for concurrent manual edits, explicit saves while Auto-save is connected and failed-write fallback; the final browser tests exercise these paths. Added newline normalization and a DIV-only paragraph-wrapper guard. Rejected its assumed `h2.editable-text` structure because the template does not generate it; single paragraph prose does not require a p wrapper, other fields preserve breaks with BRs, and leading/trailing whitespace is already normalized by capture. Recheck artifacts: FLASH_RECHECK.md and FLASH_RECHECK_RESULT.json in the same ignored directory. These were bounded static reviews; the final status changes were verified locally, not independently re-reviewed a third time.

## Limits

- The native OS save dialog was not driven end-to-end. Its success/cancel/denied-write branches were tested with a mocked picker API; actual fallback downloads and local-file reopening were tested in Edge and Firefox.
- Mobile checks use desktop browser emulation at phone widths, not physical iOS/Android hardware or Safari.
- Math rendering depends on the pinned MathJax CDN; raw LaTeX is the fallback when unavailable.
- Structural tests do not validate scientific truth, automatically detect English prose, prove complete source coverage or adjudicate image rights. Future course authoring includes those reviews.

Reproduce with commands in README.md. Screenshots, edited downloads and machine-readable results are in ignored tests/artifacts/. The clean delivered demo has none of the test edits.


## 2026-10-19 Learn-only bullet regression

- `python -m unittest discover -s tests -p 'test_*.py'`: 30 pass, including strict boolean validation and rendered editable explanation bullets.
- `python tests/browser_learn_review.py --browser edge`: pass. Learn reveals expanded bullets; Review hides them while retaining formulas, tables and genuine takeaways. Search reveals a matching hidden explanation and clearing restores Review. A real downloaded HTML preserves edited bullet text, editability and Review visibility after reopening. Mobile checks at 390 and 320 px pass without page overflow.
- Firefox run blocked at launch by missing Playwright executable `firefox-1555`; no Firefox result claimed. Test supports `--browser firefox` or `--browser all` when installed.
- Existing default blocks and template runtime are unchanged; block visibility uses existing explanation/search/export behavior.


## 23 October 2026 — focused learning depth

31 unittest tests passed. New test builds a complete valid synthetic reader with config/focused.example.toml and confirms depth metadata does not cut authored content. py_compile and Ruff passed for changed Python files. No template or runtime interaction change. A private real-course focused edition additionally passed actual Learn/Review hiding, persistent process steps, search restoration, text edit/download/reopen, offline reading and 390/320 px layout checks in installed Edge; no page errors. Private coverage/verification records remain outside Git.


## 24 October 2026 — worked-problem authoring checks

Documentation-only rule change using existing summary/steps rendering. In the real course revision, 12/12 worked blocks passed problem-before-solution and Review-visibility checks. Structural validation, existing math rendering, problem-text edit/download/reopen, zero page errors and 390/320 px overflow checks passed. A structured source comparison confirmed that only worked summaries changed; all equations, solution steps, IDs and other content remained unchanged. No renderer code changed, so no unrelated runtime regression rerun.


## 24 October 2026 — in-place worked-example audit

11 delivered course HTMLs inspected; 9 affected files corrected, comprising 69 worked-block instances. All 11 passed structural checks and 390/320 px layout checks in Edge. Affected files passed task-before-solution and actual Review visibility checks for every worked block, plus problem-text edit/download/offline reopen. Existing suite-app and suite-styles contents were checked byte-for-byte unchanged; baseline comparisons allowed only worked-summary changes. No renderer or mathematical method was changed. No new independent scientific audit claimed for this editorial restatement.


## 24 October 2026 — readable lists and emphasis

32 unit tests passed, including escaped bold input and paragraph/list grouping. tests/browser_readability.py passes clean export without false edits, actual strong/list editing, Enter-created list items, Review/search behavior, browser recovery, real export/reopen and snapshot reconcile/rebuild with inline math. Existing Edge smoke/editing, failure/picker/offline, weekly update, autosave/recovery and Learn/Review tests pass. JavaScript syntax, Python compilation and Ruff checks pass. Actual course screenshots inspected at desktop and 390/320 px widths; compact figures remain zoomable. Firefox was not run. Private course outputs stay untracked.

2026-10-24 layout correction: 32 unit tests passed. Real detailed reader checked in Edge at 2559/1440/1000/768/390/320px: no page overflow, bounded main width, matching caption/image widths, readable 640px desktop image. Figure enlargement and sidebar closure passed. Layout detector returned no findings. Three existing private editions updated by replacing only suite-styles; snapshots/content retained.

